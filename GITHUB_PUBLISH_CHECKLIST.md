# GitHub Publish Checklist

- [ ] Confirm every record in `sql/` is synthetic.
- [ ] Confirm `.env` is absent.
- [ ] Confirm no `wallet/`, `.pem`, `.p12`, `.sso`, `.key`, `.jks`, or wallet ZIP exists.
- [ ] Search the repository for database hosts, tenancy OCIDs, public IPs, passwords, API keys, tokens, personal phone/email, and employer/client confidential material.
- [ ] Run a secret scanner against the full Git history before making the repository public.
- [ ] Confirm README screenshots do not expose browser tabs, credentials, private hostnames, or customer/client information.
- [ ] Create the repository as **private first** and review it in GitHub's rendered view.
- [ ] When satisfied, switch to public and create release `v1.0`.
- [ ] Add a 3-5 minute unlisted demo-video link to README when available.
- [ ] Add the repository to LinkedIn Featured and optionally one line on the resume.
