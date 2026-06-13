# Push Workflow for my-skills

## Standard Push

```bash
cd ~/.hermes/skills/my-skills
git add .
git commit -m "更新 skills 列表"
git push
```

## Token Handling

If `git push` fails with authentication errors (token gets redacted by Hermes terminal), use a script:

```bash
#!/bin/bash
set -e
cd /home/ubuntu/.hermes/skills/my-skills

# Read token from stdin
read -r TOKEN

# Set remote and push
git remote remove origin 2>/dev/null || true
git remote add origin "https://$TOKEN@github.com/Jachin-Luo/my-skills.git"
git push -u origin main

echo "DONE"
```

Then pipe: `echo "ghp_..." | /tmp/push_my-skills.sh`

## After Push - Clean Up Token from URL

```bash
git remote set-url origin https://github.com/Jachin-Luo/my-skills.git
```

## References

- Token redaction pitfall: `github-repo-management` skill
- GitHub auth setup: `github-auth` skill
