# Skill sync

`skill_snapshot.md` is the last version of the **gtm-container-ninja** skill saved in Claude that was synced here.
A daily scheduled task compares the saved skill with this snapshot. When they differ it:

1. copies the saved skill to `SKILL.md`,
2. extracts the embedded Python script to `scripts/gtm_rename.py`,
3. updates this snapshot,
4. commits and pushes to `main`.

If nothing changed, it does nothing.
