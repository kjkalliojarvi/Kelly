Kelly
=====

Information theoretic betsize optimization for horse race betting.

How to use
==========
```bash
usage: kelly [-h] {tanaan,peli,analyysi,simu,prosentit} ...

Kelly betting

options:
  -h, --help            show this help message and exit

Commands:
  {tanaan,peli,analyysi,simu,prosentit}
    tanaan      Ravit tänään
    peli        Peli
                    'voi', 'sij', 'kak', 'duo', 'tro', 't4',
                    't5', 't64', 't65', 't75', 't86'
    analyysi    analyysi
                    'duo', 'troikka', 't4', 't5', 't6', 't7', 't8'
    simu        T-peli simulaatio
                    't4', 't5', 't64', 't65', 't75', 't86'
    prosentit   Lue prosentit
```

Examples
```bash
kelly peli 1 5 voi
    'ratakoodi 1, lähtö 5, voittaja'
kelly peli 1 4 t65 --prosentit -y
    'ratakoodi 1, lähtö 4, t65, kertoimet prosenttien perusteella, vain ylin voittoluolla'

```
