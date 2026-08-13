# Install in Codex

## Windows PowerShell

Clone the repository into the Codex skills directory:

```powershell
git clone https://github.com/xiaohan-2005/engineering-figure-gpt.git "$HOME/.codex/skills/engineering-figure-gpt"
```

Then open a new Codex session or restart Codex.

To verify that Codex can see the skill:

```powershell
Get-ChildItem "$HOME/.codex/skills/engineering-figure-gpt" -Filter "SKILL.md"
```

To update later:

```powershell
Set-Location "$HOME/.codex/skills/engineering-figure-gpt"
git pull
```

This skill is Codex-native: normal conceptual-image generation should use Codex's built-in GPT image-generation capability, so the default workflow does not require a separate image-provider wrapper in this repository.
