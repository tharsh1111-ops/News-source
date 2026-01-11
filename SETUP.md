# Git Repository Setup Guide

This guide explains how to set up and push your code to a GitHub repository.

## Step-by-Step Instructions

### 1. Navigate to Your Project Directory

Open your terminal (or Command Prompt on Windows) and navigate to your project folder:

```bash
cd "C:\Users\<username>\path\to\your\project"
```

**Note:** On Windows, you can also use forward slashes:
```bash
cd "C:/Users/<username>/path/to/your/project"
```

### 2. Check Repository Status

Verify the current state of your repository:

```bash
git status
```

This command shows:
- Which branch you're currently on
- Files that have been modified
- Files that are staged for commit
- Files that are untracked

### 3. View Recent Commit History

See the last 5 commits in a concise format:

```bash
git log --oneline -n 5
```

This displays:
- Commit hash (short form)
- Commit message
- Most recent commits first

### 4. Rename Your Branch to 'main'

Rename your current branch to 'main' (GitHub's default branch name):

```bash
git branch -M main
```

**Note:** The `-M` flag forces the rename even if a branch named 'main' already exists.

### 5. Add Remote Repository

Connect your local repository to a remote GitHub repository:

```bash
git remote add origin https://github.com/<your-username>/<repo>.git
```

Replace:
- `<your-username>` with your GitHub username
- `<repo>` with your repository name

**Example:**
```bash
git remote add origin https://github.com/<your-username>/News-source.git
```

### 6. Push to Remote Repository

Upload your code to the remote repository:

```bash
git push -u origin main
```

This command:
- Pushes your local 'main' branch to the remote 'origin'
- Sets up tracking so future pushes can use just `git push`
- The `-u` flag sets the upstream branch

## Common Issues and Solutions

### Issue: Remote already exists
If you see an error that the remote already exists:

```bash
git remote remove origin
git remote add origin https://github.com/<your-username>/<repo>.git
```

### Issue: Authentication required
If prompted for credentials:
- Use your GitHub username
- Use a Personal Access Token (PAT) instead of your password
- Or set up SSH keys for authentication

### Issue: Branch conflicts
If there are conflicts with the remote branch:

```bash
git pull origin main --rebase
# Resolve any conflicts
git push -u origin main
```

## Verifying Your Setup

After completing these steps, verify everything is configured correctly:

1. Check remote configuration:
```bash
git remote -v
```

2. Check current branch:
```bash
git branch
```

3. Check upstream tracking:
```bash
git branch -vv
```

## Additional Resources

- [GitHub Documentation](https://docs.github.com/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Desktop](https://desktop.github.com/) - GUI alternative for Git operations
