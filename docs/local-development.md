# Local Development Environment Setup

Possibilista's PostgreSQL and backend services run as Docker containers (see the root
`Dockerfile`, `backend/Dockerfile`, and `docker-compose.yml`). **Docker must be installed and
running before you follow any of the container setup steps in the main `README.md`** —
without it, `./start_postgres.sh` and `docker compose up` will fail immediately.

## Installing Docker

Pick the official guide for your OS — these are Docker's own installation instructions, not
reproduced here, since they change over time and Docker's docs are the authoritative source:

- **Windows** — [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **macOS** — [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Linux** — [Docker Engine](https://docs.docker.com/engine/install/) — follow the
  distribution-specific instructions for your distro (Ubuntu, Debian, Fedora, etc.); the
  install steps and package manager differ per distro.

Docker Desktop (Windows/macOS) requires a supported OS version and enough free RAM/disk to run
containers alongside your other work — check the requirements on the linked install page for
your OS before starting.

## Verifying installation

After installing, confirm both the Docker engine and Compose plugin are available:

```bash
docker --version
docker compose version
```

Both commands should print a version number. If either fails, Docker isn't installed correctly
or isn't on your `PATH` — revisit the install guide above for your OS.

## Troubleshooting

- **Virtualization disabled in BIOS/UEFI** (common on Windows and Intel Macs) — Docker Desktop
  needs hardware virtualization (VT-x/AMD-V) enabled; check your machine's BIOS/UEFI settings if
  Docker Desktop refuses to start.
- **Windows — WSL 2 backend** — Docker Desktop on Windows requires the WSL 2 backend. If
  prompted, run `wsl --install` and enable WSL 2 integration in Docker Desktop's settings.
- **Linux — permission denied running `docker`** — add your user to the `docker` group so you
  don't need `sudo` for every command: `sudo usermod -aG docker $USER`, then log out and back in
  for the group change to take effect.
- **Restart after installation** — if the Docker Desktop installer (or a Windows WSL 2
  integration change) prompts you to restart your machine, do so before retrying the
  verification commands above — some installs don't take effect until reboot.

## Next steps

Once `docker --version` and `docker compose version` both succeed, continue with the
"Running PostgreSQL Locally (Docker)" section in the repo root `README.md`.
