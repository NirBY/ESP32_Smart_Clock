# Publication preparation

Creality Cloud submission completed on 2026-10-24:
https://www.crealitycloud.com/model-detail/6adbce3bd4b1f991f82d5813
The platform reported that the uploaded model is being verified.

## GitHub

1. Review the working-tree cleanup and current `ESP32_Smart_Clock_3D_Design/` folder. Keep the root README link and design validation workflow in the same change. `outputs/` and generated `dist/` archives are ignored; tracked STLs, source, guide and preview images belong in Git.
2. Run `python ESP32_Smart_Clock_3D_Design/validate_all.py`, then `python ESP32_Smart_Clock_3D_Design/package_release.py`.
3. Commit and push the reviewed change. Existing Git history is retained; previous design files are removed from the current checkout.
4. Prepare an enclosure release with tag **`enclosure-v18`**. Use `GITHUB_RELEASE.md` as the description and attach the three ZIPs plus `SHA256SUMS.txt` from `dist/`. Mark it **prerelease**, and **do not mark as latest**, to keep it separate from firmware releases. The existing firmware build triggers on `v*` / `V*`; do not use those prefixes for enclosure tags.
5. Preview the draft before publishing. The design workflow validates and packages artifacts; it does not create a release or publish firmware.

Reference: [GitHub release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases).

## Creality Cloud

1. Unzip `ESP32_Smart_Clock_Creality_Upload.zip`. Upload the three individual files from `stl/` as one model group. The two fit samples may be added and labeled optional.
2. Use the title, tags and description in `CREALITY_CLOUD.md`. Select **Original**, creator **NirBY**, and **CC BY-NC-SA 4.0**. Suggested visibility is public and price is free; the creator makes these choices in the upload form.
3. The submitted covers are the English 4:3 and 3:4 multi-clock feature showcases in the repository's `docs/images/` directory. The listing also includes three real build photos, five enhanced component photos and an exploded CAD view. Display examples are illustrative.
4. Add `PRINT_GUIDE.pdf`. If the initial form does not offer PDF attachments, the model page's **Add files** flow supports adding it after upload.
5. Keep the mandatory print-pause instructions and physical-validation status in the listing. Select FFF/FDM. No machine-ready G-code or preconfigured 3MF is provided.
6. Preview the model group and its license, then publish when ready.

Official sources checked during preparation: [upload guide](https://cp.crealitycloud.com/help-center/how-to-upload-3d-models?classId=315&source=2), [supported formats](https://www.crealitycloud.com/help-center/Creality-Cloud-supported-formats), [adding a PDF](https://cp.crealitycloud.com/help-center/how-to-upload-model-pdf). The upload guide recommends square cover images and requires model-source and license choices.
