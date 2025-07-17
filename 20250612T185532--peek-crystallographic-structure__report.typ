#let title = "PEEK Crystallographic Structure"
#let date = "2025-06-12"
#let tags = "report"
#let identifier = "20250612T185532"
#let draft = true
#let mail = "stefano.marton01@universitadipavia.it"
#let lang = "it"

#import "/.resources/typst_templates/short.typ": *

#show: conf.with(
  title: title,
  author: "Stefano Marton",
  date: date,
  draft: draft,
  mail: mail,
  lang: lang,
)

// [[denote:20250611T092935]]
_Le informazioni relative alla struttura cristallina del PEEK risultano
piuttosto confuse ed in alcuni casi inconsistenti. Quanto segue si
concentra sul ricostruire il percorso storico e i risultati ottenuti._

= Obiettivi
1. Verificare l'utilizzo delle tecniche indicate in bibliografia #note(numbering: none)[Le più rilevanti sono confronto densità, DSC, micro-Raman ed XRD.]
  per la cristallinità del PEEK applicate a campioni prodotti in AM

2. Individuare tecniche facilmente applicabili e ragionevoli

3. Verificare quale approccio in XRD restituisce risultati affidabili:
  + Vale la pena Rietveld?
  + I risultati ottenuti mediante il metodo Rietveld sono significativamente differenti da quelli ottenuti per semplice integrazione?
  + Quali sono i vantaggi di uno piuttosto che l'altro?
  + Quale effetto ha l'orientazione preferenziale?

4. Utilizzare il metodo identificato come migliore per osservare: effetto sulla cristallinità di diversi parametri di stampa e diverse cariche. #note(numbering: none)[Quella che sembra essere di
    maggiore interesse è la carica con fibre di carbonio.]

= Give me PEEK.CIF please!
== Bibliografia
=== I mitici anni \'80

I primi dati disponibili risalgono al 1980
#sidecite(<dawsonXrayDataPolyaryl1980>). Viene raccolto il pattern di
diffrazione su fibra di PEEK. I riflessi ottenuti vengono indicizzati
assumendo una cella ortorombica e si individua il gruppo spaziale
_Pbcn_. Viene sottolineata la difficoltà a procedere con la
caratterizzazion vista la ridottà cristallinità (\<50%).

La cella viene solo descritta e non sono fornite immagini della
stessa. L'asse c del reticolo della cella unitaria si estende
sull'equivalente di due unità ariliche e corrisponde a 2/3 dell'unità
ripetente del polimero.

Si nota che la struttura ottenuta richiama fortemente la struttura dei
polifenilenossido, di cui i primi studi risalgono al 1969.

Nel 1984 viene pubblicato un articolo dedicato alla struttura
cristallografica del PEEK #sidecite(<n.t.wakelynPEEK1984>). Risulta
citato in tutti gli articoli successivi: in questa fonte viene per la
prima volta valutata la cella doppia. La reference in formato _.pdf_
risulta però introvabile.

Nel 1985 nel dipartimento di materiali polimerici di Tokyo
#sidecite(<shimizutakeshiCRYSTALSTRUCTUREREFRACTIVE1985>) viene
analizzata la cella cristallografica del PEEK. Sono riportate
chiaramente le posizioni atomiche ottenute, il gruppo spaziale ed i
parametri di cella. In questo caso si trova in formato _.pdf_ della reference ma
sono al quanto dubbioso sulla sua origine.

Nel 1985 un ulteriore studio sulla cristallizzazione e morfologia del
PEEK #sidecite(<kumarCrystallizationMorphologyPolyaryletheretherketone1986>)
riporta la cella che viene utilizzata per determinare il grado di
cristallinità in WAXS. Si individua la direzione (110) come direzione
di crescità preferenziale per la morfologia sferulitica caratteristica
del polimero.

#notefigure(
  image(
    "/.attachments/20250612T185532/20250618225846_screenshot.png",
    width: 65%,
  ),
  caption: [Cella ripresa da #cite(
      <kumarCrystallizationMorphologyPolyaryletheretherketone1986>,
      form: "author",
      style: "apa",
    )],
)Nel 1986 la struttura di fibre di PEEK viene raffinata
#sidecite(<fratiniRefinementStructurePEEK1986>), concentrandosi in
particolare sugli angoli di torsione tra i fenili. Vengono chiaramente
riportate le posizioni atomiche che caratterizzano la cella. Risulta
tuttavia poco chiaro come le dimensioni di cella ottenute non siano
coerenti con la cella mostrata. Vengono indicate le dimensioni della
cella contenente 2/3 dell'unità ripetente ma vengono mostrate le
immagini della cella doppia.

#notefigure(
  image(
    "/.attachments/20250612T185532/20250618230034_screenshot.png",
    width: 40%,
  ),
  caption: [Cella ripresa da #cite(
      <fratiniRefinementStructurePEEK1986>,
      form: "author",
      style: "apa",
    )],
)

=== Anni 90

Nel 1995 viene condotto uno studio
#sidecite(<jonasSynchrotronXrayScattering1995>) sfruttando luce di
sicrotrone per valutare la variazione di cristallinità del PEEK
associata alle transizioni di fase che lo caratterizzano. Ci si
concentra sulla valutazione in termini relativi e non vengono date
informazioni relativamente alla struttura cristallina.

Nel 1998 viene analizzata la variazione dei parametri di cella in
funzione della temperatura #sidecite(<jiVariationUnitCell1998>).
Conferma l'assenza di polimorfismo nel PEEK.

#figure(
  table(
    stroke: none, columns: 4, align: left, table.hline(),
    table.header([Riferimento], [a], [b], [c]), table.hline(), [#cite(
        <dawsonXrayDataPolyaryl1980>,
        form: "author",
        style: "apa",
      )],
    [7.63], [5.96], [10.0], [#cite(
        <fratiniRefinementStructurePEEK1986>,
        form: "author",
        style: "apa",
      )], [7.83], [5.94], [9.86],
    [#cite(
        <fratiniRefinementStructurePEEK1986>,
        form: "author",
        style: "apa",
      )], [7.83], [5.94], [29.58], [#cite(
        <kumarCrystallizationMorphologyPolyaryletheretherketone1986>,
        form: "author",
        style: "apa",
      )], [7.79], [5.91], [10], [#cite(
        <shimizutakeshiCRYSTALSTRUCTUREREFRACTIVE1985>,
        form: "author",
        style: "apa",
      )], [7.80], [5.92], [10], [#cite(
        <pisaniMultiscaleModelingPEEK2019>,
        form: "author",
        style: "apa",
      )], [7.75], [5.89], [9.883], table.hline()
  ),
  caption: "Parametri di
  cella riportati nelle reference raccolte",
) <tbl:cell-parameters>

=== Anni 2000

Nel 2014 sfruttando la flash DSC
#sidecite(<jinCrystallizationBehaviorMorphological2014>) è stato
proposto un modello morfoligico ben sviluppato. Si mostra l'importanza
di SAXS e AFM combinati per ottenere importanti informazioni sulla
dimensione delle sferuliti.

#figure(
  image(
    "/.attachments/20250612T185532/20250618210928_screenshot.png",
    width: 70%,
  ),
  caption: [Modello morfologico ripreso da #cite(
      <jinCrystallizationBehaviorMorphological2014>,
      form: "author",
      style: "apa",
    )],
)

Si conferma l'utilizzo della cella contenente 2/3 dell'unità
ripetente, a maggior ragione a fronte dell'organizzazione del modello
che rende quindi la cella doppia sostanzialmente obsoleta.

Nel 2019 viene condotto uno studio esteso sul calcolo delle proprietà
del PEEK mediante dinamica molecolare e micromeccanica
#sidecite(<pisaniMultiscaleModelingPEEK2019>). Viene indicata
chiaramente la gerarchia di sviluppo dei cristalli di PEEK.

Nel 2020 viene condotto uno studio sulla microstruttura del PEEK
irradiato da radiazioni gamma, sfruttando GISAXS
#sidecite(<liStudyMicrostructurePolyether2020>). Ci si concentra
solamente sull'aspetto microstrutturale.

== Conclusioni sullo stato attuale dell'arte

Le informazioni cristallografiche al momento utilizzate risultano quelle indicate da #cite(<fratiniRefinementStructurePEEK1986>, form: "prose", style: "apa").
Come già osservato insieme si riscontrano una serie di criticità.

La cella indicata inizialmente è quella con le dimensioni riportate
all'interno della @tbl:cell-parameters. Vengono però riportate le
posizioni atomiche della cella doppia, sono indicati 38 atomi di
carbonio, 6 atomi di ossigeno e 38 atomi di idrogeno, in un volume di
cella pari a 1375.771 $Å^3$.

$
  rho & = (n dot M)/(N_A dot V) \
      & = ((6 dot 16 g/"mol" + 38 dot 12
          g/"mol" + 38 dot g/"mol") dot 8)/(6.022 dot 10^23 dot 1.3757 dot
        10^(-21) "cm"^3)        \
      & = 5.6974 g/"cm"^3       \
$

Ne risulta una densità più di 4 volte superiore sia a quella indicata
nell'articolo stesso sia a quella misurabile sperimentalmente.

Al momento la problematica rimane irrisolta, seppure costruendo atomo
per atomo si riesce ad ottenere qualcosa di sensato. Osservando invece
il lavoro prodotto in giappone #cite(
  <shimizutakeshiCRYSTALSTRUCTUREREFRACTIVE1985>,
  form: "author",
  style: "apa",
)

#notefigure(
  image(
    "/.attachments/20250612T185532/20250618223937_screenshot.png",
    width: 70%,
  ),
  label: <fig:cella-giapponesi>,
  caption: [Cella costruitac con le informazion riportate da #cite(
      <shimizutakeshiCRYSTALSTRUCTUREREFRACTIVE1985>,
      form: "author",
      style: "apa",
    )],
);Costruendo la cella con i dati disponibili in si ottiene il _.cif_
che sembra avere senso, osservabile in @fig:cella-giapponesi.

Si può procedere poi a costruire la supercella a partire dalla cella primitiva, indicata in @fig:cella-multipla #notefigure(
  image(
    "/.attachments/20250612T185532/20250618224109_screenshot.png",
    width: 50%,
  ),
  caption: [Supercella costruita a partire dalla cella indicata nel lavoro di #cite(
      <shimizutakeshiCRYSTALSTRUCTUREREFRACTIVE1985>,
      form: "author",
      style: "apa",
    )],
  label: <fig:cella-multipla>,
)

La cella multipla, in ogni caso, sembra essere stata storicamente
abbandonata in favore della cella di dimensioni ridotte. Questo a
fronte anche dei modelli morfologici sviluppati negli ultimi
vent'anni.

In ogni caso, nei lavori che utilizzando XRD per la determinazione
della cristallinità non si spendono a valutare quanto sia
effettivamente corretto il dato ottenuto. Seppur come in quanto
ottenuto in uno studio comparativo
#sidecite(<doumengComparativeStudyCrystallinity2021>) si osserva
chiaramente un discostamento importante tra i valori di cristallinità
ottenuti con tecniche diverse.

Le informazioni ottenute utilizzando luce di sincrotrone si
concentrano principalmente sull'aspetto microstrutturale, come
osservato nelle refence sopra citate. Tuttavia questo aspetto risulta
da me ancora poco approfondito.

= Lavoro svolto fin'ora

== Dati ottenuti

=== Sovrapposto globale

Sovrapponendo tutti i pattern ottenuti si osserva coerenza sia in
termini di intensità che di posizione dei picchi.

#figure(
  image("plots/sovrapposto_tutti.png", width: 90%),
  caption: [Sovrapposto di tutti i diffrattogrammi ottenuti],
)

Non si osservano discostamenti evidenti tra il gruppo di campioni stampati con il profilo _amorfo_ e stampati con il profilo _cristallino_.
Tuttavia procedendo in questo modo non mi sembra si riesca ad apprezzare ne la differenza di forma ne la differenza di intensità.

#pagebreak()

=== Sovrapposto gruppo amorfo e cristallino

Vengono osservati il gruppo amorfo e il gruppo cristallino separatamente.

#wideblock(grid(
  columns: 2,
  figure(
    image("plots/sovrapposto_amorfo.png", width: 70%),
    caption: [Campioni stampati con il profilo _amorfo_],
  ),
  figure(
    image("plots/sovrapposto_cristallino.png", width: 70%),
    caption: [Campioni stampati con il profilo _cristallino_],
  ),
))
Si osserva distintamente una differenza nel profilo dei picchi nella regione tra 18 e 22 gradi. Il picco nel gruppo di campioni stampati con profilo _cristallino_ il picco risulta più affilato, così come anche quell compreso nella regione tra 27 e 30 gradi.

=== Confronto amorfo e cristallino

Si osserva il sovrapposto di ciascuna posizione del piatto di stampa confrontando quanto ottenuto.

#wideblock(grid(
  columns: 2,
  figure(
    image("plots/sovrapposto_confronto-piatto-3-cristallino.png", width: 70%),
    caption: [Campioni stampati con il profilo _cristallino_],
  ),
  figure(
    image("plots/sovrapposto_confronto-piatto-3-amorfo.png", width: 70%),
    caption: [Campioni stampati con il profilo _amorfo_],
  ),
))

Non si osservano differenze significative per campioni stampati nelle
stesse condizioni sia nel caso di profilo amorfo che nel caso di
profilo cristallino.

#pagebreak()

Vengono inoltre confrontati i pattern ottenuti nelle medesime
posizioni nel piatto 3 utilizzando profilo amorfo e profilo
cristallino.

#wideblock(figure(
  grid(
    columns: 2,
    column-gutter: -70pt,
    image("plots/sovrapposto_confronto-piatto-3-posizione-1.png", width: 70%),
    image("plots/sovrapposto_confronto-piatto-3-posizione-2.png", width: 70%),

    image("plots/sovrapposto_confronto-piatto-3-posizione-3.png", width: 70%),
    image("plots/sovrapposto_confronto-piatto-3-posizione-4.png", width: 70%),
  ),
  caption: [Sovrapposto delle 4 posizioni di stampa nel piatto 3],
))

Il profilo _cristallino_ osservando il confronto dettagliato determina
un'intensità dei picchi maggiore in modo consistente in tutte e 4 le
posizioni.

=== Background

Si riporta il pattern ottenuto per il background.

#figure(image("plots/G000_5-40-0.01-1000ms.png", width: 70%))

#pagebreak()

=== Rietveld

Lanciando un Rietveld su quanto ottenuto fin'ora quanto si osserva sembra funzionare.

#wideblock(figure(
  image(
    "/.attachments/20250612T185532/20250623221241_screenshot.png",
    width: 100%,
  ),
  caption: [Test preliminare raffinamento Rietveld],
))


In particolare:

1. È stata inserita una _dummy phase_ amorfa

2. Le posizioni dei riflessi hanno senso

3. La proporzione tra intensità dei picchi ha senso

Sembra osseravabile orientazione preferenziale a giudicare dal riflesso (111) e da quanto discusso in bibliografia, anche se osservando il background non mi esporrei oltre. Mi risulta al momento difficile identificare il ruolo del riflesso appartenente al background.


== Domande aperte

1. Sarebbe sensato mediare i valori ottenuti?
2. Ho provato a procedere con _WinPlotR_ al calcolo della cristallinità, rimango piuttosto perplesso dalla scelta dei tagli e della baseline.
3. Ma come è possibile che siano ancora ritenuti validi valori ottenuti nel 1986? Seppur altri tipi di caratterizzazioni siano state condotte perchè non è stata determinata la cella e le posizioni atomiche con maggior accuratezza?
