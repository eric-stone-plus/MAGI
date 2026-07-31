#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "scripts/host/lib/seat_artifacts.py"
COMPOSE_PROFILE = ROOT / "scripts/host/lib/compose_profile.py"
PYTHON = sys.executable
ROUTE_BINDING_TEST_FIELDS = {
    "party_id", "route_id", "adapter", "executable", "family", "provider",
    "text_model", "multimodal_model", "perspective",
}


def run_helper(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run([PYTHON, *args], check=check, capture_output=True, text=True)


class HostContracts(unittest.TestCase):
    def test_seat_configs_and_policies_are_exact_production_bindings(self) -> None:
        expected = {
            "seat-m": ("mimo", "xiaomi", "mimo-v2.5-pro", "https://api.xiaomimimo.com/v1", "mimo"),
            "seat-d": ("deepseek", "deepseek", "deepseek-v4-pro", "https://api.deepseek.com/v1", "reasonix"),
            "seat-g": ("openai", "openai-api", "gpt-5.6-sol", "https://apinebula.com/v1", "codex"),
        }
        for seat_id, (family, provider, model, base_url, adapter) in expected.items():
            seat_path = ROOT / f"container/seats/{seat_id}.json"
            policy_path = ROOT / f"container/policies/{seat_id}.json"
            seat = json.loads(seat_path.read_text())
            policy = json.loads(policy_path.read_text())
            self.assertEqual((seat["model_family"], seat["provider"], seat["text_model"], seat["provider_base_url"]), (family, provider, model, base_url))
            run_helper(str(ARTIFACTS), "validate", "seat", str(seat_path))
            run_helper(str(ARTIFACTS), "validate", "policy", str(policy_path), "--seat", str(seat_path))
            routes = [*policy["roster"], policy["counterpart_arbiter"], policy["primary_arbiter"]]
            self.assertEqual(len(routes), 7)
            self.assertTrue(policy["auto_primary_arbiter"])
            self.assertEqual({route["adapter"] for route in routes}, {adapter})
            self.assertEqual({route["family"] for route in routes}, {family})
            self.assertEqual({route["text_model"] for route in routes}, {model})
            self.assertEqual(len({route["route_id"] for route in routes}), 7)
            self.assertEqual(len({route["perspective"] for route in routes}), 7)

    def test_policy_validation_rejects_binding_and_role_drift(self) -> None:
        seat_path = ROOT / "container/seats/seat-g.json"
        source = json.loads((ROOT / "container/policies/seat-g.json").read_text())
        mutations = []
        for field, value in (("adapter", "mimo"), ("family", "deepseek"), ("text_model", "other")):
            candidate = copy.deepcopy(source); candidate["roster"][0][field] = value; mutations.append(candidate)
        candidate = copy.deepcopy(source); candidate["roster"][1]["route_id"] = candidate["roster"][0]["route_id"]; mutations.append(candidate)
        candidate = copy.deepcopy(source); candidate["roster"][1]["perspective"] = candidate["roster"][0]["perspective"]; mutations.append(candidate)
        candidate = copy.deepcopy(source); candidate["roster"] = candidate["roster"][:-1]; mutations.append(candidate)
        candidate = copy.deepcopy(source); candidate["auto_primary_arbiter"] = False; mutations.append(candidate)
        with tempfile.TemporaryDirectory() as temp:
            for index, candidate in enumerate(mutations):
                path = Path(temp) / f"policy-{index}.json"
                path.write_text(json.dumps(candidate))
                result = run_helper(str(ARTIFACTS), "validate", "policy", str(path), "--seat", str(seat_path), check=False)
                self.assertNotEqual(result.returncode, 0, f"mutation {index} was accepted")

    def test_original_brief_contract_is_closed_before_mount(self) -> None:
        source = {
            "brief_version": "1.1", "question": "q", "context": None,
            "evidence_roots": [], "snapshot_ignore": [], "attachments": [],
            "action_scope": None, "affected_paths": [], "action_binding_sha256": None,
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "brief.json"
            path.write_text(json.dumps(source))
            run_helper(str(ARTIFACTS), "validate", "brief", str(path))
            source["extra"] = "not allowed"
            path.write_text(json.dumps(source))
            rejected = run_helper(str(ARTIFACTS), "validate", "brief", str(path), check=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("closed-field mismatch", rejected.stderr)

    def test_compose_has_per_seat_allowlist_sidecars_and_hardening(self) -> None:
        text = (ROOT / "container/compose.yml").read_text()
        for token in ("read_only: true", "cap_drop: [ALL]", "no-new-privileges:true", "ipc: private", "MAGI_CONTAINER_UID", "MAGI_CONTAINER_GID"):
            self.assertIn(token, text)
        for seat, host in (("m", "api.xiaomimimo.com"), ("d", "api.deepseek.com"), ("g", "apinebula.com")):
            self.assertIn(f"seat-{seat}-private", text)
            self.assertIn(f"http://seat-{seat}-egress:3128", text)
            proxy = (ROOT / f"container/proxy/seat-{seat}.cfg").read_text()
            self.assertIn(f"allow * * {host} 443 HTTP_CONNECT", proxy)
            self.assertIn("deny *", proxy)
            self.assertNotIn("auth none", proxy)
        self.assertIn("final-adjudicator:", text)
        self.assertIn("final-adjudicator-private", text)
        self.assertIn("final-adjudicator-egress", text)
        self.assertIn("MAGI_SEAT_MODE: final", text)
        self.assertIn("final_adjudicator_provider_api_key", text)
        self.assertEqual(text.count("internal: true"), 4)
        self.assertEqual(text.count("nc -z 127.0.0.1 3128"), 4)
        self.assertEqual(text.count("condition: service_healthy"), 4)
        self.assertEqual(text.count("http_proxy: http://seat-"), 3)
        self.assertEqual(text.count("https_proxy: http://seat-"), 3)
        self.assertEqual(text.count("target: provider_api_key"), 4)
        self.assertNotIn("host.docker.internal", text)
        self.assertNotIn("MAGI_SEAT_M_EGRESS_PROXY", text)
        self.assertNotIn("ANTHROPIC", text)
        self.assertNotRegex(text, r"\.omp|\.claude|\.codewhale|auth\.json")
        self.assertEqual(text.count("MAGI_EVIDENCE_ROOT:-${MAGI_ORIGINAL_BRIEF}"), 3)
        self.assertEqual(text.count("MAGI_ASSIGNMENT_PLAN:-${MAGI_ORIGINAL_BRIEF}"), 3)

    def test_entrypoint_uses_detached_auto_pa_polling_only(self) -> None:
        text = (ROOT / "container/entrypoint.sh").read_text()
        self.assertIn('run --brief "$ART/quinte-brief.json" --json', text)
        self.assertIn('status "$RUN_ID" --json', text)
        self.assertIn('waiting_primary_arbiter) cancel_and_fail', text)
        self.assertIn('degraded|failed|failed_policy|cancelled)', text)
        self.assertIn('cancel "$RUN_ID" --json', text)
        self.assertIn('validate policy "$POLICY" --seat "$SEAT_CONFIG"', text)
        self.assertIn('validate brief "$INPUT"', text)
        self.assertIn('assignment plan does not bind the mounted seat', text)
        self.assertIn('policy validate --json', text)
        self.assertIn('cd "$PROFILE_HOME"', text)
        self.assertIn("COMPOSITION.json", text)
        self.assertIn('MAGI_SEAT_MODE: final', (ROOT / "container/compose.yml").read_text())
        self.assertIn('"$MODE" = final', text)
        self.assertIn("/final-input/packet.json", text)
        self.assertIn("/final-output/verdict.json", text)
        self.assertIn("magi-agent", text)
        self.assertNotIn("PA_HANDOFF", text)
        self.assertNotIn("PA_TIMEOUT_SECONDS", text)
        self.assertNotIn("--wait", text)
        self.assertNotRegex(text, r"\bquinte\b.*\bwait\b")

    def test_finale_launcher_uses_compose_final_adjudicator(self) -> None:
        text = (ROOT / "scripts/host/magi-seat.sh").read_text()
        self.assertIn("final_agent_mode()", text)
        self.assertIn("export_finale_compose_placeholders()", text)
        self.assertIn('docker compose -f "$COMPOSE" run --rm final-adjudicator', text)
        self.assertIn("final-adjudicator-egress", text)
        self.assertIn("MAGI_REQUIRED_IMAGE_DIGEST", text)
        self.assertIn("reconcile_declared_and_observed", text)
        self.assertIn(
            "MAGI_REQUIRED_IMAGE_DIGEST must be set to the frozen execution.image_digest pin",
            text,
        )
        self.assertNotIn('"$ROOT/bin/magi-agent"', text.split("final_agent_mode()")[1].split("case \"${1:-}\"")[0])

    def test_finale_only_env_can_render_compose_config(self) -> None:
        """Compose must load with the exact env final_agent_mode exports (no seat tree).

        Sibling seat services are not started, but their ${VAR:?} expansions still
        run when Docker Compose parses the project file.
        """

        if not shutil.which("docker"):
            self.skipTest("docker unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            secret = root / "secret"
            secret.write_text("test-secret\n", encoding="utf-8")
            secret.chmod(0o600)
            config = ROOT / "container" / "seats" / "seat-g.json"
            packet = root / "packet.json"
            packet.write_text("{}", encoding="utf-8")
            packet.chmod(0o400)
            output = root / "out"
            output.mkdir()
            # Minimal dirs so profile volume paths exist even if compose inspects them.
            env = os.environ.copy()
            env.update(
                {
                    "MAGI_CONTAINER_UID": str(os.getuid()),
                    "MAGI_CONTAINER_GID": str(os.getgid()),
                    "MAGI_CODE_ROOT": str(ROOT),
                    "MAGI_FINAL_CONFIG": str(config),
                    "MAGI_FINAL_SECRET_FILE": str(secret),
                    "MAGI_FINAL_PACKET": str(packet),
                    "MAGI_FINAL_OUTPUT": str(output),
                    "MAGI_ORIGINAL_BRIEF": str(packet),
                    "MAGI_EVIDENCE_ROOT": str(output),
                    "MAGI_ASSIGNMENT_PLAN": str(packet),
                    "MAGI_ARTIFACT_ROOT": str(output),
                    "MAGI_SEAT_M_PROFILE": str(output),
                    "MAGI_SEAT_D_PROFILE": str(output),
                    "MAGI_SEAT_G_PROFILE": str(output),
                    "MAGI_SEAT_M_CONFIG": str(config),
                    "MAGI_SEAT_D_CONFIG": str(config),
                    "MAGI_SEAT_G_CONFIG": str(config),
                    "MAGI_SEAT_M_POLICY": str(ROOT / "container" / "policies" / "seat-m.json"),
                    "MAGI_SEAT_D_POLICY": str(ROOT / "container" / "policies" / "seat-d.json"),
                    "MAGI_SEAT_G_POLICY": str(ROOT / "container" / "policies" / "seat-g.json"),
                    "MAGI_SEAT_M_SECRET_FILE": str(secret),
                    "MAGI_SEAT_D_SECRET_FILE": str(secret),
                    "MAGI_SEAT_G_SECRET_FILE": str(secret),
                    "MAGI_REVIEW_PACKET_M": str(packet),
                    "MAGI_REVIEW_PACKET_D": str(packet),
                    "MAGI_REVIEW_PACKET_G": str(packet),
                    "MAGI_REVIEW_OUTPUT_M": str(output),
                    "MAGI_REVIEW_OUTPUT_D": str(output),
                    "MAGI_REVIEW_OUTPUT_G": str(output),
                }
            )
            # Without placeholders, compose fails (sibling ${MAGI_ORIGINAL_BRIEF:?...}).
            bare = env.copy()
            for key in (
                "MAGI_ORIGINAL_BRIEF",
                "MAGI_ARTIFACT_ROOT",
                "MAGI_SEAT_M_PROFILE",
                "MAGI_SEAT_M_CONFIG",
                "MAGI_SEAT_M_POLICY",
            ):
                bare.pop(key, None)
            rejected = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(ROOT / "container" / "compose.yml"),
                    "config",
                    "--quiet",
                ],
                env=bare,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(rejected.returncode, 0, rejected.stderr)
            self.assertTrue(
                "MAGI_ORIGINAL_BRIEF" in rejected.stderr
                or "MAGI_SEAT_M" in rejected.stderr
                or "required variable" in rejected.stderr.lower()
                or rejected.returncode != 0
            )
            completed = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(ROOT / "container" / "compose.yml"),
                    "config",
                    "--quiet",
                ],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stderr or completed.stdout,
            )
            # Require the rendered project includes final-adjudicator.
            rendered = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(ROOT / "container" / "compose.yml"),
                    "config",
                ],
                env=env,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("final-adjudicator", rendered.stdout)

    def test_final_agent_requires_image_digest_pin(self) -> None:
        """final-agent must refuse to launch without MAGI_REQUIRED_IMAGE_DIGEST."""

        env = os.environ.copy()
        env.pop("MAGI_REQUIRED_IMAGE_DIGEST", None)
        with tempfile.TemporaryDirectory() as temporary:
            secret = Path(temporary) / "secret"
            secret.write_text("x\n", encoding="utf-8")
            secret.chmod(0o600)
            env["MAGI_FINAL_SECRET_FILE"] = str(secret)
            env["MAGI_FINAL_CONFIG"] = str(ROOT / "container" / "seats" / "seat-g.json")
            completed = subprocess.run(
                ["bash", str(ROOT / "scripts" / "host" / "magi-seat.sh"), "final-agent"],
                input='{"task":"magi_final_adjudication"}\n',
                text=True,
                capture_output=True,
                env=env,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("MAGI_REQUIRED_IMAGE_DIGEST", completed.stderr)

    def test_dockerfile_has_only_stateless_production_harnesses(self) -> None:
        text = (ROOT / "container/Dockerfile").read_text()
        for token in ("@mimo-ai/cli@0.1.6", "reasonix@1.17.17", "@openai/codex@0.145.0", "USER node"):
            self.assertIn(token, text)
        for token in ("claude", "anthropic", "oh-my-pi", "codewhale", "opencode", "kilo", "kimi-chat"):
            self.assertNotIn(token, text.lower())

    def test_profile_composition_preserves_private_rules_and_lockdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base"; overlay = root / "overlay"; destination = root / "composed"
            (base / "skills/domain").mkdir(parents=True); (base / "hooks").mkdir()
            (base / "memories").mkdir()
            (base / "SOUL.md").write_text("# Base\n## 输出格式\nkeep output\n## 授权与写入\nkeep auth\n## 自写封印\nkeep seal\n")
            (base / "skills/domain/SKILL.md").write_text("PRIVATE_DOMAIN_RULE_SENTINEL\n")
            (base / "hooks/privacy.py").write_text("PRIVATE_PRIVACY_SENTINEL\n")
            (base / "hooks/privacy.py").chmod(0o700)
            (base / "memories/MEMORY.md").write_text("IMMUTABLE_MEMORY_SENTINEL\n")
            agents = root / "AGENTS.md"
            agents.write_text("GitHub repositories\nWorkspace layout\nHermes self-write lockdown\nPRIVATE_AUTHORIZATION_SENTINEL\n")
            config = root / "config.yaml"
            config.write_text(
                f"memory:\n  memory_enabled: true\nskills:\n  write_approval: false\ncurator:\n  enabled: true\n"
                "self_improvement:\n  enabled: true\nplatform_toolsets:\n  cli: [memory, skills, web]\n"
                "fallback_providers:\n  - provider: forbidden-secondary\n    model: secondary-model\n"
                "fallback_model:\n  provider: forbidden-legacy\n  model: legacy-model\n"
                f"hooks:\n  pre_tool_call:\n    - command: {base}/hooks/privacy.py --mode strict --label 'two words'\n"
                "voice:\n  record_key: secret-value\nmcp_servers:\n  unsafe: {}\n"
            )
            config.chmod(0o600)
            overlay.mkdir(); (overlay / "SOUL.md").write_text("# Formalist Independent Expert Profile\nFORMALIST_SENTINEL\n")
            (overlay / "profile.json").write_text(json.dumps({
                "profile_version":"1.0", "profile_id":"formalist", "discipline":"d", "epistemic_lens":"e",
                "methods":["m"], "failure_checks":["f"], "instructions":"i"
            }))
            run_helper(str(COMPOSE_PROFILE), "compose", "--technical-base", str(base), "--technical-agents", str(agents), "--technical-config", str(config), "--overlay", str(overlay), "--destination", str(destination), "--seat", "seat-m")
            run_helper(str(COMPOSE_PROFILE), "validate", str(destination), "--seat", "seat-m")
            self.assertIn("PRIVATE_DOMAIN_RULE_SENTINEL", (destination / "skills/domain/SKILL.md").read_text())
            self.assertIn("PRIVATE_PRIVACY_SENTINEL", (destination / "hooks/privacy.py").read_text())
            self.assertTrue((destination / "hooks/privacy.py").stat().st_mode & 0o100)
            self.assertIn("IMMUTABLE_MEMORY_SENTINEL", (destination / "memories/MEMORY.md").read_text())
            self.assertIn("PRIVATE_AUTHORIZATION_SENTINEL", (destination / "AGENTS.md").read_text())
            self.assertIn("FORMALIST_SENTINEL", (destination / "SOUL.md").read_text())
            receipt = json.loads((destination / "COMPOSITION.json").read_text())
            self.assertEqual(set(receipt), {"base_sha256", "composition_version", "overlay_sha256", "profile_id", "seat_id", "composed_content_sha256"})
            rendered = (destination / "config.yaml").read_text()
            for token in ("memory_enabled: false", "user_profile_enabled: false", "write_approval: true", "enabled: false", "no_mcp"):
                self.assertIn(token, rendered)
            self.assertNotIn("unsafe:", rendered)
            self.assertIn("disabled_toolsets:", rendered)
            rendered_config = __import__("yaml").safe_load(rendered)
            self.assertEqual(rendered_config["platform_toolsets"]["cli"], ["no_mcp"])
            self.assertIn("web", rendered_config["agent"]["disabled_toolsets"])
            self.assertEqual(rendered_config["fallback_providers"], [])
            self.assertNotIn("fallback_model", rendered_config)
            self.assertEqual(
                shlex.split(rendered_config["hooks"]["pre_tool_call"][0]["command"]),
                [
                    "python3",
                    "/runtime/hermes-home/profiles/magi-seat/hooks/privacy.py",
                    "--mode",
                    "strict",
                    "--label",
                    "two words",
                ],
            )
            self.assertIn("/runtime/hermes-home/profiles/magi-seat/hooks/privacy.py", rendered)
            self.assertNotIn(str(base), rendered)
            self.assertNotIn("secret-value", rendered)
            profile = json.loads((destination / "profile.json").read_text())
            self.assertNotIn("seat_id", profile)
            self.assertNotIn("composition_version", profile)
            run_helper(str(ARTIFACTS), "validate", "profile", str(destination / "profile.json"), "--expected-id", "formalist")

            # An unchanged composition is reusable, but changed inputs fail closed.
            run_helper(str(COMPOSE_PROFILE), "compose", "--technical-base", str(base), "--technical-agents", str(agents), "--technical-config", str(config), "--overlay", str(overlay), "--destination", str(destination), "--seat", "seat-m")
            os.chmod(base / "SOUL.md", 0o600)
            with (base / "SOUL.md").open("a") as handle: handle.write("changed source\n")
            changed = run_helper(str(COMPOSE_PROFILE), "compose", "--technical-base", str(base), "--technical-agents", str(agents), "--technical-config", str(config), "--overlay", str(overlay), "--destination", str(destination), "--seat", "seat-m", check=False)
            self.assertNotEqual(changed.returncode, 0)
            self.assertIn("different source content", changed.stderr)

            os.chmod(destination / "SOUL.md", 0o600)
            with (destination / "SOUL.md").open("a") as handle: handle.write("tampered\n")
            result = run_helper(str(COMPOSE_PROFILE), "validate", str(destination), "--seat", "seat-m", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("content digest mismatch", result.stderr)

    def test_composed_validation_rejects_fallbacks_and_bare_python_hooks(self) -> None:
        spec = importlib.util.spec_from_file_location("magi_compose_profile", COMPOSE_PROFILE)
        self.assertIsNotNone(spec); self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        locked = {
            "self_improvement": {"enabled": False},
            "memory": {"memory_enabled": False, "user_profile_enabled": False, "write_approval": True},
            "skills": {"write_approval": True},
            "curator": {"enabled": False},
            "platform_toolsets": {"cli": ["no_mcp"]},
            "agent": {"disabled_toolsets": module.SEAT_DISABLED_TOOLSETS.copy()},
            "mcp_servers": {},
            "fallback_providers": [],
            "hooks": {"pre_tool_call": [{"command": "python3 /runtime/hook.py --strict"}]},
        }
        module._verify_lockdown(locked)
        for mutation in (
            {"fallback_providers": [{"provider": "other", "model": "other"}]},
            {"fallback_model": {"provider": "legacy", "model": "legacy"}},
            {"hooks": {"pre_tool_call": [{"command": "/runtime/hook.py --strict"}]}},
        ):
            candidate = copy.deepcopy(locked); candidate.update(mutation)
            with self.assertRaises(module.CompositionError):
                module._verify_lockdown(candidate)

    def test_profile_composition_rejects_secrets_symlinks_runtime_and_missing_rules(self) -> None:
        source = (ROOT / "scripts/host/lib/compose_profile.py").read_text()
        for token in (".env", "state.db", "sessions", "profile symlink is forbidden", "technical AGENTS.md is missing required categories"):
            self.assertIn(token, source)

    def test_dossier_binds_policy_manifest_result_and_seat(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run_dir = root / "quinte-run"
            (run_dir / "input").mkdir(parents=True)
            seat_path = ROOT / "container/seats/seat-m.json"
            policy_path = ROOT / "container/policies/seat-m.json"
            seat = json.loads(seat_path.read_text())
            policy = json.loads(policy_path.read_text())
            profile_path = root / "profile.json"
            profile_path.write_text((ROOT / "profiles/formalist/profile.json").read_text())
            reviewer_profile = root / "reviewer-profile"
            reviewer_profile.mkdir()
            for name, content in {
                "profile.json": profile_path.read_text(),
                "SOUL.md": "immutable formalist profile\n",
                "AGENTS.md": "immutable technical rules\n",
                "config.yaml": "memory:\n  memory_enabled: false\n",
            }.items():
                (reviewer_profile / name).write_text(content)
            import hashlib
            hasher = hashlib.sha256()
            for path in sorted(path for path in reviewer_profile.rglob("*") if path.is_file()):
                relative = path.relative_to(reviewer_profile).as_posix().encode()
                data = path.read_bytes()
                hasher.update(len(relative).to_bytes(8, "big")); hasher.update(relative)
                hasher.update(len(data).to_bytes(8, "big")); hasher.update(data)
            (reviewer_profile / "COMPOSITION.json").write_text(json.dumps({
                "base_sha256": "sha256:" + "a" * 64,
                "composition_version": "1.0",
                "overlay_sha256": "sha256:" + "b" * 64,
                "profile_id": "formalist",
                "seat_id": "seat-m",
                "composed_content_sha256": "sha256:" + hasher.hexdigest(),
            }))
            thesis_path = root / "thesis.json"
            thesis_path.write_text(json.dumps({
                "thesis_version": "1.0", "question": "q", "thesis": "t",
                "claims": [{"id": "C1", "statement": "s", "evidence_refs": [], "uncertainty": "u", "boundary": "b"}],
                "recommendation": "r", "limitations": [],
            }))
            perspective_path = root / "perspective-input.json"
            perspective_path.write_text(json.dumps({
                "perspective_input_version": "1.0", "seat_id": "seat-m",
                "original_brief_sha256": "sha256:" + "1" * 64, "profile_id": "formalist",
                "profile_sha256": "sha256:" + "2" * 64, "thesis_sha256": "sha256:" + "3" * 64,
                "original_question": "q", "action_scope": None, "affected_paths": [],
                "action_binding_sha256": None, "derived_context": "c",
            }))
            (run_dir / "input/policy.json").write_text(json.dumps(policy))
            routes = [*policy["roster"], policy["counterpart_arbiter"], policy["primary_arbiter"]]
            bindings = [{key: route[key] for key in ROUTE_BINDING_TEST_FIELDS} for route in routes]
            binding = {
                "seat_id": seat["seat_id"], "family": seat["model_family"], "provider": seat["provider"],
                "text_model": seat["text_model"], "multimodal_model": seat["multimodal_model"],
            }
            brief_digest = "sha256:" + "4" * 64
            manifest = {"status": "completed", "manifest_version": "2.0", "brief_sha256": brief_digest, "seat_binding": binding, "route_bindings": bindings}
            result = {"status": "completed", "result_version": "2.1", "brief_sha256": brief_digest, "seat_binding": binding, "route_bindings": bindings}
            (run_dir / "manifest.json").write_text(json.dumps(manifest))
            (run_dir / "result.json").write_text(json.dumps(result))
            output = root / "dossier.json"
            command = [str(ARTIFACTS), "dossier", "--seat", str(seat_path), "--profile", str(profile_path), "--reviewer-profile", str(reviewer_profile), "--thesis", str(thesis_path), "--perspective", str(perspective_path), "--run-dir", str(run_dir), "--output", str(output)]
            run_helper(*command)
            self.assertTrue(output.is_file())

            result["seat_binding"] = {**binding, "family": "deepseek"}
            (run_dir / "result.json").write_text(json.dumps(result))
            rejected = run_helper(*command, check=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("seat bindings differ", rejected.stderr)

    def test_launchers_use_seat_work_dynamic_ids_and_private_composition(self) -> None:
        shell = (ROOT / "scripts/host/magi-seat.sh").read_text()
        powershell = (ROOT / "scripts/host/magi-seat.ps1").read_text()
        self.assertIn("$trial/seat-work", shell)
        self.assertIn("$(id -u)", shell); self.assertIn("$(id -g)", shell)
        self.assertIn("trial-private/composed-profiles", shell)
        self.assertIn("trial-private/composed-profiles", powershell)
        self.assertIn("'1000'", powershell)
        self.assertNotIn("EgressProxy", powershell)
        self.assertNotIn("--egress-proxy", shell)
        self.assertIn("seat_artifacts.py\" validate policy", shell)
        self.assertIn("seat_artifacts.py\" validate brief", shell)
        self.assertIn("assigned evidence manifest digest mismatch", shell)
        self.assertIn("assigned assignment plan digest mismatch", shell)
        self.assertIn('export MAGI_EVIDENCE_ROOT=', shell)
        self.assertIn('MAGI_ASSIGNMENT_PLAN=', shell)
        self.assertIn("compose_profile.py", shell)
        self.assertIn("wait_for_proxy", shell)
        self.assertIn("did not become healthy", powershell)
        self.assertNotIn("--no-deps", shell)
        self.assertNotIn("--no-deps", powershell)

    def test_no_private_content_is_checked_into_public_profiles(self) -> None:
        tracked_text = "\n".join(path.read_text(errors="ignore") for path in (ROOT / "profiles").rglob("*") if path.is_file())
        self.assertNotIn("PRIVATE_DOMAIN_RULE_SENTINEL", tracked_text)
        self.assertNotIn("/Users/ericstone/Private", tracked_text)
        for profile in (ROOT / "profiles").iterdir():
            self.assertEqual({path.name for path in profile.iterdir()}, {"SOUL.md", "profile.json"})

    def test_current_source_lock_is_reviewed_and_fail_closed_on_drift(self) -> None:
        lock = (ROOT / "container/source-lock.env").read_text()
        build = (ROOT / "scripts/host/build-image.sh").read_text()
        locked = next(
            line.split("=", 1)[1]
            for line in lock.splitlines()
            if line.startswith("QUINTE_COMMIT=")
        )
        self.assertRegex(locked, r"^[0-9a-f]{40}$")
        subprocess.run(
            ["git", "-C", str(ROOT.parent / "QUINTE"), "cat-file", "-e", f"{locked}^{{commit}}"],
            check=True,
            capture_output=True,
        )
        self.assertIn("lacks run manifest 2.0", build)
        self.assertIn("mandatory egress proxy", build)
        self.assertIn("automatic Primary Arbiter", build)
        self.assertIn("require_adapter_branch reasonix", build)
        self.assertIn("require_adapter_branch codex", build)
        self.assertNotIn("AdapterKind::Reasonix", build)
        self.assertNotIn("AdapterKind::Codex", build)

    def test_build_sources_have_single_authoritative_locations(self) -> None:
        build = (ROOT / "scripts/host/build-image.sh").read_text()
        self.assertIn('$HOME/Private/agent-design/hermes/agent', build)
        self.assertIn('/Users/ericstone/Public/QUINTE', build)
        self.assertNotIn('Private/agent-design/QUINTE', build)
        self.assertNotIn('Private/agent-design/MAGI', build)


if __name__ == "__main__":
    unittest.main()
