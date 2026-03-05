# HARMONIX

**A harmonization pipeline framework for polysomnography data**

HARMONIX is an open-source framework for harmonizing PSG data for public distribution via the [National Sleep Research Resource (NSRR)](https://sleepdata.org). Built on top of [Luna](https://zzz-luna.org/luna/), it compresses a 5–7 day harmonization process into a single day.

📖 **Documentation:** https://TejasKarkera10.github.io/harmonix

---

## Quick start

```bash
git clone https://github.com/TejasKarkera10/harmonix
cd harmonix
pip install -e .

harmonix scaffold --dataset mydata --path /path/to/working/dir
harmonix phi --sl sl/s0.lst
harmonix cmap --sl sl/s0.lst
harmonix qc --sl sl/s0.lst --jobs 20
harmonix coverage --res res/
harmonix issues --res res/
harmonix report --readme README.md
```

## Status

Under active development. See [docs](https://TejasKarkera10.github.io/harmonix) for current tool status.

## License

MIT
