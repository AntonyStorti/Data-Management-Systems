# Creare il Cluster

E' molto semplice: 

PREREQUISITO --> "Avere installato <b>Docker</b> sulla propria macchina!"

1) Scaricate il contenuto di questa directory.
2) Accedete a tale cartella dal terminale.
3) Lanciate il comando <i>make install</i>

<b><u>N.B.</u></b> <br>
Per compatibilità con eventuali installazioni locali di MongoDB, i nodi nel <i>Cluster</i> ascoltano sulla <b>Porta 27018</b> e non su quella di default 27017 !!!

## Struttura del Cluster

<b><u>N.B.</u></b> <br>
Si prega di notare che esso non è adatto ad un uso reale in ambiente Enterprise, ma, solo per le fasi di sviluppo e di test,o, di piccoli scenari applicativi!

<br>

La struttura del <i>Cluster</i>, per ragioni computazionali, è molto basilare.
Nonostante ciò esso è completo sotto ogni punto di vista (<i>Sharding, Replica Set, ecc...</i>)

<br>

E' così costituita:

1) Una instanza di <i>Mongos</i> --> <b>1 Router</b>
2) Tre instanze di <i>Mongod</i> --> <b>3 Shards</b>
3) Tre servers di configurazione

<br>

<div align="center">
<img width="611" alt="Screenshot 2024-10-20 alle 12 01 27" src="https://github.com/user-attachments/assets/8844da1b-5942-4e02-993a-97363f1ce80a">
</div>

<br>

<div align="center">
<img width="661" alt="Screenshot 2024-10-20 alle 12 03 07" src="https://github.com/user-attachments/assets/5ca0e47b-0538-40ab-b522-20bfb6341321">
</div>

## Sharding e Replica Sets

Le seguenti immagini, fanno comprendere come il <i>Cluster</i> gestisce tali aspetti:

<br>

<div align="center">
<img width="661" alt="Screenshot 2024-10-20 alle 12 03 22" src="https://github.com/user-attachments/assets/29f334ee-6c27-430c-8125-3ea5bb807fa0">
</div>

<br>

<div align="center">
<img width="611" alt="Screenshot 2024-10-20 alle 12 02 15" src="https://github.com/user-attachments/assets/d02b272a-f661-4638-abb4-1cebf4ac9855">
</div>

<br>

<div align="center">
<img width="611" alt="Screenshot 2024-10-20 alle 12 02 27" src="https://github.com/user-attachments/assets/892ec13a-c772-4d2c-84ab-ea3d46661828">
</div>
