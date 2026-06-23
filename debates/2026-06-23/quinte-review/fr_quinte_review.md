# Revue externe de QUINTE v3.4 · Audit MAGI

> **Objet** : `~/Public/QUINTE/specs/PROTOCOL.md` (v3.4, 2026-06-20)  
> **Auditeur** : MAGI en qualité de tiers externe  
> **Référence MAGI** : `~/Public/MAGI/specs/PROTOCOL.md` (v3.4, 2026-06-20)  
> **Date de revue** : 2026-06-23  
> **Méthode** : lecture intégrale du spécimen QUINTE, confrontation mot-à-mot avec le spécimen MAGI, vérification des documents satellites (`CHANGELOG.md`, `README.md`, `MIGRATION.md`, `specs/theoretical-foundation.md`, `specs/security-assumptions.md`, `specs/extensions.md`) et inspection partielle de l’arborescence `debates/`.

---

## Résumé exécutif

Le spécimen QUINTE v3.4 est techniquement riche mais souffre d’une **dérive spécifique** caractéristique : accumulation de mécanismes v3.4 (JSON sidecar, pseudonymes R2, suivi des changements d’avis, classification 6 niveaux, substitution agent→MAGI, QUINTE récursif) sans revalidation structurelle. L’audit a identifié **6 contradictions internes majeures**, **4 références manquantes à MAGI**, **5 incohérences de version**, **5 axes de scope creep**, **5 zones de complexité superflue** et **3 incompatibilités directes avec le spécimen MAGI**. La plus grave est une contradiction sur **qui tranche la convergence MAGI** : QUINTE affirme que MAGI s’auto-tranche en Mode B sans hm, alors que le spécimen MAGI donne explicitement ce pouvoir à hm.

---

## 1. Contradictions internes

### 1.1 Nombre d’agents en R2 : 3 ou 5 ?

- **§1.1** (ligne 31 du spécimen) : R2 est décrit comme « 5 elements (cc + hm + cw + omp + rx) ».
- **§1.1** (ligne 36) : le mode anonyme R2 utilise les pseudonymes « Participant A/B/C/D/E », ce qui correspond bien à 5 agents.
- **§3.3** (lignes 150-155) : « For each disputed claim, **3 refutation agents** cross-review », avec un vote ≥2/3, 1/3, 0/3.
- **§3.3** (ligne 157) : « Cross-model requirement : at least **1 refuter** uses a different provider/model ».

**Problème** : le spécimen ne précise jamais comment les 5 agents de R2 se mappent sur les « 3 refutation agents ». Les 2 agents supplémentaires sont-ils des observateurs ? Des relecteurs passifs ? La règle « 1 refuter sur 3 » est-elle compatible avec un pool de 5 ? Cette ambiguïté rend la Phase 3 non implémentable sans interprétation arbitraire.

### 1.2 Substitution agent→MAGI : après épuisement des retries, sauf quand non

- **§1.1** (ligne 33) : « Substitution only after retries are exhausted. »
- **§4.8** (ligne 302) : pour la classe `deprecated`, la récupération est « ⛔ Skip agent → substitution » sans retry.

**Problème** : la table de classification court-circuite la règle générale. Si un agent est `deprecated`, on saute directement à la substitution, ce qui contredit l’affirmation « substitution only after retries are exhausted ». Le spécimen ne résout pas cette priorité.

### 1.3 Timeout R1 : 120 s ou 180 s ?

- **§1.1** (ligne 134) : « R1 all launch in parallel. Timeout **120s** → kill + shrink prompt + retry. »
- **`specs/extensions.md`** (ligne 34) : « The **180s** threshold is the protocol default. »
- **§4.8** (ligne 299) : classe `timeout` — « 0 bytes after deadline » sans valeur numérique, mais « shrink prompt ≤400 chars » (alors que §1.1 ne précise pas la taille de shrink).

**Problème** : deux seuils de timeout coexistent (120 s et 180 s) sans explication de contexte. Le lecteur ne sait pas lequel prime.

### 1.4 MAGI converge seul… ou pas

- **§1.3** (lignes 66-67) : « hm retains veto over Phase outputs but does NOT adjudicate MAGI's internal convergence gate during R1 Mode B. MAGI delegates self-converge (≥2/3 gate). »
- **§4.5** (lignes 267-279) : décrit la convergence interne MAGI sans mentionner le rôle de hm, ni la séparation affirmée en §1.3.

**Problème** : §1.3 établit une règle de gouvernance spécifique au Mode B, mais §4.5 l’omet. Un implémenteur qui lit uniquement §4.5 ne connaîtra pas cette séparation. C’est une contradiction par omission.

### 1.5 Pseudonymes R2 : 5 lettres pour 3 refuters

- **§1.1** (ligne 36) : pseudonymes A/B/C/D/E (5 participants).
- **§3.3** (lignes 150-157) : 3 refutation agents seulement.

**Problème** : mêmes contradictions que 1.1, répétées dans deux sections différentes. Le spécimen ne stabilise jamais le modèle de R2.

### 1.6 Push gate / 憲門 : exigence déclarée versus composant inexistant

- **§5.6** (ligne 331) : « Any push (code, config, docs) requires prior QUINTE (R1+R2+R3). No exceptions. »
- **§6 憲門** (ligne 346) : contrôle BANNIN-enforced pré-écriture, référence à HIGHBALL.
- **`specs/theoretical-foundation.md`** (ligne 121) : « BANNIN is specification-only (as of 2026-06-19). »
- **`specs/security-assumptions.md`** (lignes 133, 145) : BANNIN est soumis à une circularité d’auto-exécution et son « specification-only status » est qualifié de risque résiduel le plus important.

**Problème** : l’Invariant #6 (« Push gate ») est présenté comme impératif, mais son mécanisme d’exécution (BANNIN/KENGEN) n’est pas implémenté. C’est une contradiction entre la norme et la réalité opérationnelle.

---

## 2. Références manquantes à MAGI

### 2.1 Aucune référence locale au spécimen MAGI

- **§1.4** (ligne 82) et **`README.md`** (ligne 79) : la seule référence au spécimen MAGI est une URL GitHub externe (`https://github.com/eric-stone-plus/MAGI/blob/main/specs/PROTOCOL.md`).
- **Absence** : aucun lien relatif local du type `../../MAGI/specs/PROTOCOL.md`, pourtant les deux dépôts sont frères sous `~/Public/`.

**Problème** : une revue offline ou un clone local ne peut pas résoudre la référence. Cela fragilise la traçabilité cross-repo.

### 2.2 Pas de référence à `MAGI/specs/theoretical-foundation.md`

- **`specs/theoretical-foundation.md`** de QUINTE (lignes 147-149) cite bien MAGI, mais le spécimen `PROTOCOL.md` ne renvoie jamais à la fondation théorique de MAGI pour les mécanismes MAGI (hétérogénéité, convergence, substitution).

**Problème** : les sections QUINTE sur MAGI (§1.4, §4.5) sont des redites qui pourraient diverger de la source canonique MAGI.

### 2.3 `hermes-core-rules-mac-x86/SOUL.md` non résoluble

- **§5.8** (ligne 333) : « See hermes-core-rules-mac-x86/SOUL.md. »
- **Absence** : pas de chemin absolu, pas de lien relatif, et ce dépôt n’est pas présent dans `~/Public/` selon l’inspection.

**Problème** : référence orpheline. L’« iron law » repose sur un document inaccessible.

### 2.4 Référence HIGHBALL sans chemin local

- **§6 憲門** (ligne 346) : « Defined in HIGHBALL `specs/kennomon-architecture-gate.md` (ratified 2026-06-19) » sans chemin local `../../HIGHBALL/...`.

**Problème** : même type d’orchestration cross-repo que pour MAGI ; seule l’URL n’est même pas fournie ici.

---

## 3. Incohérences de version

### 3.1 Répertoires `debates/` référencés mais inexistants

- **`CHANGELOG.md`** v3.4 (ligne 15) : « See `debates/2026-06-20-magi-borrowings/` and `debates/2026-06-20-magi-landscape/`. »
- **Inspection** : le répertoire `~/Public/QUINTE/debates/` ne contient pas de dossier daté du 2026-06-20 (les dates les plus récentes vont jusqu’au 2026-06-17).

**Problème** : référence à des preuves d’audit absentes. Cela remet en cause la traçabilité des changements v3.4.

### 3.2 `MIGRATION.md` obsolète

- **`MIGRATION.md`** (ligne 23) : décrit le protocole comme « implementation-agnostic specification ».
- **Spécimen `PROTOCOL.md`** (ligne 7) : « It is not implementation-agnostic — it depends on Hermes-specific primitives (terminal for agent dispatch, memory+skill for cross-session invariant enforcement, cron for autonomous triggering, terminal for Phase 6 cross-match). »

**Problème** : `MIGRATION.md` contredit le positionnement actuel du protocole. Document non maintenu.

### 3.3 `theoretical-foundation.md` daté du 18 juin pour un sync v3.4 du 20 juin

- **`specs/theoretical-foundation.md`** (ligne 4) : « Version: 1.0 (2026-06-18) ».
- **Spécimen `PROTOCOL.md`** (ligne 5) : v3.4 synchronisée avec MAGI v3.4 le 2026-06-20.
- **`CHANGELOG.md`** (ligne 14) : v3.4 ajoute Invariants #7-9 et synchronise avec MAGI v3.4.

**Problème** : la fondation théorique ne porte pas la version 3.4 malgré son rôle de « canonical spec ». Cela crée un doute sur la couverture des nouveaux invariants v3.4 dans la fondation théorique.

### 3.4 Sauts de version dans l’historique MAGI

- **`~/Public/MAGI/specs/PROTOCOL.md`** §6 (lignes 161-166) : versions 2.0 → 3.0 → 3.1 → 3.4, toutes sur 2026-06-17/19/20. Les versions 3.2 et 3.3 sont absentes, alors que QUINTE les possède.

**Problème** : bien que la « sync v3.4 » soit revendiquée, les historiques de version ne sont pas alignés. Un lecteur ne peut pas reconstruire la correspondance exacte QUINTE 3.2/3.3 ↔ MAGI.

### 3.5 Badge README et titre du spécimen

- **`README.md`** (ligne 15) : badge `protocol-v3.4-blue`.
- **`MIGRATION.md`** (ligne 21) : mentionne un badge `protocol-v2.4` corrigé en v3.0.

**Problème** : mineur, mais `MIGRATION.md` reste ancré sur une ancienne correction de badge plutôt que sur l’état v3.4 actuel.

---

## 4. Scope creep

### 4.1 QUINTE récursif (Phase 7)

- **§7** (lignes 198-227) : ajoute une sous-débat complète (R1+R2+R3) avec conditions de déclenchement, isolation, ré-injection, annotation `[QUINTE↻ N]`.

**Problème** : la complexité d’un débat QUINTE complet est dupliquée récursivement sans preuve que les bénéfices justifient le coût. Aucune métrique de profondeur maximale ou de coût total n’est fournie.

### 4.2 Multiplication des phases

Le protocole compte désormais : Phase -1, 0, 1, 2, 3, 4, 5, 5a, 6, 7 — soit **10 phases**. Chacune avec ses propres règles, seuils, formats et approbations hm.

**Problème** : la surface d’implémentation et de maintenance devient très grande. Le risque d’omission ou de bug de séquence augmente exponentiellement.

### 4.3 Empilement v3.4 non revalorisé

En une seule version, QUINTE ajoute :
- JSON sidecar + validation des citations (§2) ;
- Pseudonymes R2 + révélation R3 (§1.1, §3.3) ;
- Suivi des changements d’avis R2 (§1.1, §3.3) ;
- Classification 6 niveaux des erreurs (§4.8) ;
- Table de substitution agent→MAGI (§1.1, §4.8) ;
- Récupération de session Grok (§4.8) ;
- Vérification de cohérence cross-repo (§4.9) ;
- Mode B MAGI et substitution (§1.1, §4.5).

**Problème** : aucune section ne justifie pourquoi tous ces mécanismes appartiennent à la même version plutôt qu’à des itérations séparées.

### 4.4 Extension du protocole à toutes les écritures

- **§5.6 Push gate** : tout push nécessite QUINTE.
- **§5.8 MAGI before file modification** : hm ne peut pas écrire sans MAGI.

**Problème** : QUINTE passe d’un protocole de débat à un contrôleur d’écriture généralisé. Cela dépasse le périmètre originel et repose sur BANNIN qui n’est pas implémenté.

### 4.5 Dépendance à HIGHBALL/BANNIN non résolue

- **§6 憲門** et **§5.6/5.8** font référence à BANNIN/KENGEN comme mécanismes d’exécution.
- **`theoretical-foundation.md`** et **`security-assumptions.md`** admettent que BANNIN est « specification-only ».

**Problème** : le périmètre fonctionnel de QUINTE s’étend vers l’enforcement, mais l’enforcement n’existe pas.

---

## 5. Complexité superflue

### 5.1 Triple format de sortie R1

- **§2** impose :
  1. un corps markdown lisible par l’homme ;
  2. un JSON sidecar structuré `{verdict, confidence, reasoning_chain, evidence_citations}` ;
  3. un « R1 Schema (loose mode) » avec `claims`, `coverage`, `uncertainties`, etc.

**Problème** : trois formats différents pour le même agent. Le parseur de Phase 2 doit gérer markdown + JSON sidecar + fallback regex. C’est une source majeure de fragilité.

### 5.2 Pseudonymes R2 + cérémonie de révélation

- **§1.1** et **§3.3** : les agents R2 sont anonymisés A/B/C/D/E, puis révélés en R3.

**Problème** : aucune preuve empirique n’est fournie que cette anonymisation réduit le biais de marque. En contrepartie, elle ajoute de la coordination, du parsing et une étape de révélation.

### 5.3 Suivi des changements d’avis avec format forcé

- **§1.1** (ligne 37) : les agents doivent signaler « CHANGED: [old position] BECAUSE [evidence from agent X] ».
- **§3.3** (ligne 159) : R3 pondère les avis modifiés plus fort.

**Problème** : le format forcé est fragile (dépend de l’auto-rapport de l’agent) et la pondération en R3 n’est pas quantifiée.

### 5.4 Nomenclature japonaise des cinq portes

- **§6** : 雨門 Amamon, 鏡門 Kyōmon, 證門 Shōmon, 閂門 Kan’nukimon, 憲門 Kennōmon.

**Problème** : chaque porte possède un nom kanji, une romanisation et une traduction anglaise. Cela enrichit la narration mais complique la documentation et les grep sans ajouter de sémantique technique.

### 5.5 Classification 6 niveaux avec comportements provider-spécifiques

- **§4.8** (lignes 292-314) : six classes d’erreur avec retry/backoff/skip/substitution différenciés, plus des notes spécifiques (kimi 80 % thinking tax, grok `--resume`, cc auth.json nested key).

**Problème** : la table est si spécifique aux providers qu’elle ressemble plus à une procédure d’exploitation qu’à une spécification de protocole. Elle est susceptible de changer à chaque mise à jour de CLI.

---

## 6. Affirmations sur MAGI incompatibles avec le spécimen MAGI

### 6.1 Qui tranche la convergence MAGI ?

- **QUINTE §1.3** (lignes 66-67) : « hm retains veto over Phase outputs but does NOT adjudicate MAGI's internal convergence gate during R1 Mode B. MAGI delegates self-converge (≥2/3 gate). »
- **MAGI §2.4** (lignes 91-100) : « hm reads all three outputs. Binary decision: ≥2/3 agree → Converge / ≤1/3 agree → Diverge. No weighted voting. No confidence score. Binary gate. »

**Problème critique** : QUINTE retire à hm le pouvoir de trancher la convergence interne de MAGI en Mode B, alors que le spécimen MAGI donne explicitement ce pouvoir à hm. C’est une contradiction fondamentale de gouvernance. Si QUINTE a raison, le spécimen MAGI est obsolète. Si MAGI a raison, QUINTE crée un mécanisme d’auto-convergence non prévu par MAGI.

### 6.2 Annotation de confiance en Mode A

- **QUINTE §1.4** (ligne 76) : « ≥2/3 converge → answer with confidence annotation ».
- **MAGI §2.4** (ligne 100) : « No weighted voting. No confidence score. Binary gate. »

**Problème** : QUINTE attribue à MAGI Mode A une annotation de confiance que le spécimen MAGI interdit explicitement. (Note : le `README.md` de MAGI mentionne une annotation 2/3=moderate, 3/3=high, mais le spécimen canonique `PROTOCOL.md` de MAGI l’interdit. QUINTE s’aligne sur le README, pas sur le spécimen.)

### 6.3 Exclusivité Mode A/B versus déploiement anytime de MAGI

- **QUINTE §1.4** (ligne 80) : « Mode A and Mode B are mutually exclusive per session. »
- **MAGI §6 Version History** (ligne 165) : v3.1 (2026-06-20) introduit « Anytime deployment : MAGI doctors dispatchable independently or collectively at any QUINTE phase or outside it — on-demand analysis, agent fallback, filesystem exploration, second opinion. Mode A/B remain but non-exhaustive. »

**Problème** : QUINTE considère Mode A et B comme mutuellement exclusifs et exhaustifs, alors que le spécimen MAGI affirme explicitement que A/B ne sont « non-exhaustive » et que les docteurs MAGI peuvent être déployés à n’importe quelle phase. QUINTE ignore cette extension v3.1 de MAGI.

### 6.4 Points de convergence (non-problématiques, notés pour exhaustivité)

Les éléments suivants sont cohérents entre QUINTE et MAGI et ne sont pas des défauts :
- Table de substitution agent→MAGI (QUINTE §4.8 / MAGI §2.5) : identique.
- Annotation `[MAGI N/3]` (QUINTE §2 / MAGI §2.4) : identique.
- Markdown comme sortie principale de convergence, JSON consommé par QUINTE Phase 2 (QUINTE §2 / MAGI §2.3) : identique.
- `website/` comme sous-repo git indépendant (QUINTE §4.9 / MAGI §2.6) : identique.
- Déclenchement par hm, pas par l’utilisateur (QUINTE §1.4 / MAGI §2.1) : identique.

---

## 7. Synthèse de sévérité

| Catégorie | Nombre | Sévérité maximale | Détail |
|-----------|--------|-------------------|--------|
| Contradictions internes | 6 | 🔴 Critique | Nombre d’agents R2, timeout, substitution, adjudication MAGI, push gate |
| Références manquantes | 4 | 🟠 Majeur | MAGI local, SOUL.md, HIGHBALL local, fondation théorique MAGI |
| Incohérences de version | 5 | 🟠 Majeur | Debates absents, MIGRATION obsolète, fondation v1.0 datée, sauts MAGI |
| Scope creep | 5 | 🟡 Modéré | QUINTE récursif, 10 phases, extension aux écritures, BANNIN non implémenté |
| Complexité superflue | 5 | 🟡 Modéré | Triple format, pseudonymes, suivi d’avis, noms japonais, table 6 niveaux |
| Incompatibilités MAGI | 3 | 🔴 Critique | Adjudication convergence, score de confiance, exhaustivité Mode A/B |

---

## 8. Recommandations

1. **Résoudre la contradiction sur l’adjudication MAGI** : choisir entre « MAGI s’auto-converge » et « hm tranche la convergence », puis aligner QUINTE et MAGI.
2. **Stabiliser le modèle R2** : décider si R2 comporte 3 refuters ou 5 participants, et réécrire §1.1 et §3.3 de manière cohérente.
3. **Uniformiser les timeouts** : choisir entre 120 s (§1.1) et 180 s (`extensions.md`) et documenter les exceptions.
4. **Ajouter des références locales** : remplacer ou compléter les URL GitHub par des chemins relatifs (`../../MAGI/specs/PROTOCOL.md`, `../../HIGHBALL/specs/kennomon-architecture-gate.md`).
5. **Mettre à jour ou retirer `MIGRATION.md`** : corriger l’affirmation « implementation-agnostic » ou archiver le document.
6. **Créer les répertoires d’audit manquants** ou supprimer les références aux debates/2026-06-20.
7. **Clarifier le push gate / 憲門** : tant que BANNIN n’est pas implémenté, ne pas présenter ces règles comme des invariants exécutables.
8. **Simplifier les formats de sortie R1** : fusionner ou hiérarchiser le JSON sidecar et le « loose schema ».
9. **Aligner la notion de confiance MAGI** : supprimer l’annotation de confiance de QUINTE si MAGI reste sur une porte binaire, ou réviser MAGI pour l’autoriser explicitement.
10. **Documenter l’intégration MAGI v3.1 « anytime deployment »** : QUINTE doit reconnaître que les docteurs MAGI peuvent être déployés en dehors de Mode A/B stricts.

---

*Audit rédigé sine ira et studio.*  
*MAGI v3.4 — revue externe de QUINTE v3.4 — 2026-06-23*
