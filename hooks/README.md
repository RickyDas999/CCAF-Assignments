# Hook Scenarios

Quick reference for picking the right Claude Code hook, worked through five scenarios.

## 1. Block direct pushes to `main`

**Scenario:** Your team must never let an agent push directly to the main branch.

**Answer:** Use `PreToolUse`. It needs to block the action.

## 2. Notify when a long job finishes

**Scenario:** You want a Slack message whenever a long-running job finishes.

**Answer:** Use `Notification`. No blocking needed.

## 3. Audit trail of everything attempted

**Scenario:** You need an audit trail of everything an agent attempted last Tuesday, including anything that was refused.

**Answer:** Use `Stop`. No blocking — just summarize each turn.

## 4. Fix inconsistent date formats

**Scenario:** A tool returns dates in three different formats and the agent keeps misreading them.

**Answer:** Use `PostToolUse`. It needs to block so it can fix the output before the agent reads it.

## 5. "Just return 0 so it stops asking for permission"

**Scenario:** A teammate says: *"Add a hook that returns 0 so our pipeline stops asking for permission."* Is that going to work?

**Answer:** No. Returning 0 only removes the hook's own objection — it doesn't grant permissions. The pipeline can still be blocked by other permission checks.
