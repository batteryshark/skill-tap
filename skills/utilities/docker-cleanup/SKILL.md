---
name: docker-cleanup
description: "Survey and safely reclaim Docker disk usage with category-specific confirmation, export options, and platform-aware virtual disk handling."
---

# Clean Up Docker Safely

1. Run `bin/docker-cleanup survey` and record Docker's total/reclaimable space plus stopped containers, dangling images, unused volumes, and build cache separately.
2. Read [references/cleanup-policy.md](references/cleanup-policy.md). Offer export/inspection for containers or images whose purpose is unclear.
3. Obtain category-specific approval. Never infer approval for volumes, `docker system prune -a`, or deletion from a general request to free space.
4. Run only approved prune commands and repeat the survey.
5. On Windows/WSL, compact the Docker VHDX only after pruning, a clean WSL shutdown, explicit elevation, and discovery of the actual disk path. On macOS, use Docker Desktop's supported reclaim behavior for the installed version.

Use [agents/cleanup-reviewer.md](agents/cleanup-reviewer.md) when persistent data or an unfamiliar environment is involved.
