#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Carte Gourmande - recuperation des photos - METHODE MULTI-SOURCES (celle qui avait marche).
Pour chaque produit, essaie DANS L'ORDRE :
  1) Wikipedia FR (image de l'article)
  2) variantes du nom
  3) Wikimedia Commons
  4) Wikipedia EN
Telecharge avec un vrai User-Agent de navigateur, redimensionne 800px, optimise.
Saute les images deja presentes (REPREND ou il s'est arrete).

A lancer sur ton Mac, dans le dossier qui contient tes images (et data.js) :
    python3 images3.py

(Liste ITEMS generee automatiquement depuis data.js -- 859 fiches.)
"""
import io, os, time, requests
from PIL import Image

UA = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36",
      "Referer":"https://fr.wikipedia.org/"}
MAXPX, QUALITY, PAUSE = 800, 82, 0.6
BACKOFF=[20,40,60,90]

ITEMS = [
  {
    "name": "Kouign-amann",
    "file": "kouign-amann.jpg"
  },
  {
    "name": "Caramel au beurre salé",
    "file": "caramel-au-beurre-sale.jpg"
  },
  {
    "name": "Palet breton de Pont-Aven",
    "file": "palet-breton-de-pont-aven.jpg"
  },
  {
    "name": "Galette sablée bretonne",
    "file": "galette-sablee-bretonne.jpg"
  },
  {
    "name": "Far breton",
    "file": "far-breton.jpg"
  },
  {
    "name": "Sardines en boîte de Douarnenez",
    "file": "sardines-en-boite-de-douarnenez.jpg"
  },
  {
    "name": "Crêpe bretonne",
    "file": "crepe-bretonne.jpg"
  },
  {
    "name": "Sel de Guérande",
    "file": "sel-de-guerande.jpg"
  },
  {
    "name": "Andouille de Vire",
    "file": "andouille-de-vire.jpg"
  },
  {
    "name": "Tripes à la mode de Caen",
    "file": "tripes-a-la-mode-de-caen.jpg"
  },
  {
    "name": "Caramels d'Isigny",
    "file": "caramels-disigny.jpg"
  },
  {
    "name": "Confiture de lait de Rouen",
    "file": "confiture-de-lait-de-rouen.jpg"
  },
  {
    "name": "Camembert de Normandie",
    "file": "camembert-de-normandie.jpg"
  },
  {
    "name": "Neufchâtel",
    "file": "neufchatel.jpg"
  },
  {
    "name": "Livarot",
    "file": "livarot.jpg"
  },
  {
    "name": "Pont-l'Évêque",
    "file": "pont-l-eveque.jpg"
  },
  {
    "name": "Calisson d'Aix",
    "file": "calisson-daix.jpg"
  },
  {
    "name": "Navettes de Marseille",
    "file": "navettes-de-marseille.jpg"
  },
  {
    "name": "Tapenade marseillaise",
    "file": "tapenade-marseillaise.jpg"
  },
  {
    "name": "Papaline d'Avignon",
    "file": "papaline-davignon.jpg"
  },
  {
    "name": "Fruits confits d'Apt",
    "file": "fruits-confits-dapt.jpg"
  },
  {
    "name": "Berlingot de Carpentras",
    "file": "berlingot-de-carpentras.jpg"
  },
  {
    "name": "Pâte de fruits de Saint-Didier",
    "file": "pate-de-fruits-de-saint-didier.jpg"
  },
  {
    "name": "Fleur de sel d'Aigues-Mortes",
    "file": "fleur-de-sel-daigues-mortes.jpg"
  },
  {
    "name": "Huile d'olive de Nice",
    "file": "huile-dolive-de-nice.jpg"
  },
  {
    "name": "Tourtons de Champsaur",
    "file": "tourtons-de-champsaur.jpg"
  },
  {
    "name": "Fougasse provençale",
    "file": "fougasse-provencale.jpg"
  },
  {
    "name": "Gibassié de Provence",
    "file": "gibassie-de-provence.jpg"
  },
  {
    "name": "Miel de lavande de Provence",
    "file": "miel-de-lavande-de-provence.jpg"
  },
  {
    "name": "Riz de Camargue",
    "file": "riz-de-camargue.jpg"
  },
  {
    "name": "Thym de Provence",
    "file": "thym-de-provence.jpg"
  },
  {
    "name": "Banon",
    "file": "banon.jpg"
  },
  {
    "name": "Violette de Toulouse",
    "file": "violette-de-toulouse.jpg"
  },
  {
    "name": "Cachou Lajaunie",
    "file": "cachou-lajaunie.jpg"
  },
  {
    "name": "Cassoulet de Castelnaudary",
    "file": "cassoulet-de-castelnaudary.jpg"
  },
  {
    "name": "Cassoulet de Toulouse",
    "file": "cassoulet-de-toulouse.jpg"
  },
  {
    "name": "Cassoulet de Carcassonne",
    "file": "cassoulet-de-carcassonne.jpg"
  },
  {
    "name": "Mongetada de Saint-Gaudens",
    "file": "mongetada-de-saint-gaudens.jpg"
  },
  {
    "name": "Saucisse de Toulouse",
    "file": "saucisse-de-toulouse.jpg"
  },
  {
    "name": "Ail rose de Lautrec",
    "file": "ail-rose-de-lautrec.jpg"
  },
  {
    "name": "Échaudé de Carmaux",
    "file": "echaude-de-carmaux.jpg"
  },
  {
    "name": "Anchois de Collioure",
    "file": "anchois-de-collioure.jpg"
  },
  {
    "name": "Zézette de Sète",
    "file": "zezette-de-sete.jpg"
  },
  {
    "name": "Rousquilles du Roussillon",
    "file": "rousquilles-du-roussillon.jpg"
  },
  {
    "name": "Cannelé bordelais",
    "file": "cannele-bordelais.jpg"
  },
  {
    "name": "Piment d'Espelette",
    "file": "piment-despelette.jpg"
  },
  {
    "name": "Truffe du Périgord",
    "file": "truffe-du-perigord.jpg"
  },
  {
    "name": "Foie gras du Sud Ouest",
    "file": "foie-gras-du-sud-ouest.jpg"
  },
  {
    "name": "Pruneaux d'Agen",
    "file": "pruneaux-dagen.jpg"
  },
  {
    "name": "Touron Basque",
    "file": "touron-basque.jpg"
  },
  {
    "name": "Pastis landais",
    "file": "pastis-landais.jpg"
  },
  {
    "name": "Piperade basque",
    "file": "piperade-basque.jpg"
  },
  {
    "name": "Sauce béarnaise",
    "file": "sauce-bearnaise.jpg"
  },
  {
    "name": "Noisettines du Médoc",
    "file": "noisettines-du-medoc.jpg"
  },
  {
    "name": "Sarments du Médoc",
    "file": "sarments-du-medoc.jpg"
  },
  {
    "name": "Noix du Périgord",
    "file": "noix-du-perigord.jpg"
  },
  {
    "name": "Fuet catalan",
    "file": "fuet-catalan.jpg"
  },
  {
    "name": "Pélardon",
    "file": "pelardon.jpg"
  },
  {
    "name": "Roquefort",
    "file": "roquefort.jpg"
  },
  {
    "name": "Laguiole",
    "file": "laguiole.jpg"
  },
  {
    "name": "Rocamadour",
    "file": "rocamadour.jpg"
  },
  {
    "name": "Massepain de Saint-Léonard-de-Noblat",
    "file": "massepain-de-saint-leonard-de-noblat.jpg"
  },
  {
    "name": "Tourteau fromagé",
    "file": "tourteau-fromage.jpg"
  },
  {
    "name": "Farci poitevin",
    "file": "farci-poitevin.jpg"
  },
  {
    "name": "Macaron de Montmorillon",
    "file": "macaron-de-montmorillon.jpg"
  },
  {
    "name": "Broyé du Poitou",
    "file": "broye-du-poitou.jpg"
  },
  {
    "name": "Bêtise de Cambrai",
    "file": "betise-de-cambrai.jpg"
  },
  {
    "name": "Gaufre fourrée lilloise",
    "file": "gaufre-fourree-lilloise.jpg"
  },
  {
    "name": "Pastille du mineur",
    "file": "pastille-du-mineur.jpg"
  },
  {
    "name": "Macaron d'Amiens",
    "file": "macaron-damiens.jpg"
  },
  {
    "name": "Maroilles",
    "file": "maroilles.jpg"
  },
  {
    "name": "Madeleine de Commercy",
    "file": "madeleine-de-commercy.jpg"
  },
  {
    "name": "Biscuit rose de Reims",
    "file": "biscuit-rose-de-reims.jpg"
  },
  {
    "name": "Nonnette de Reims",
    "file": "nonnette-de-reims.jpg"
  },
  {
    "name": "Pain d'épice d'Alsace",
    "file": "pain-depice-dalsace.jpg"
  },
  {
    "name": "Bretzel alsacien",
    "file": "bretzel-alsacien.jpg"
  },
  {
    "name": "Saucisse de Strasbourg (knack)",
    "file": "saucisse-de-strasbourg-knack.jpg"
  },
  {
    "name": "Pâtes Spätzle",
    "file": "pates-spatzle.jpg"
  },
  {
    "name": "Cramaillotte (miel de pissenlit)",
    "file": "cramaillotte-miel-de-pissenlit.jpg"
  },
  {
    "name": "Andouillette de Troyes",
    "file": "andouillette-de-troyes.jpg"
  },
  {
    "name": "Munster",
    "file": "munster.jpg"
  },
  {
    "name": "Chaource",
    "file": "chaource.jpg"
  },
  {
    "name": "Langres",
    "file": "langres.jpg"
  },
  {
    "name": "Moutarde de Dijon",
    "file": "moutarde-de-dijon.jpg"
  },
  {
    "name": "Escargots de Bourgogne",
    "file": "escargots-de-bourgogne.jpg"
  },
  {
    "name": "Anis de Flavigny",
    "file": "anis-de-flavigny.jpg"
  },
  {
    "name": "Gougère bourguignonne",
    "file": "gougere-bourguignonne.jpg"
  },
  {
    "name": "Saucisse de Morteau",
    "file": "saucisse-de-morteau.jpg"
  },
  {
    "name": "Coussin de Lyon",
    "file": "coussin-de-lyon.jpg"
  },
  {
    "name": "Quenelle lyonnaise",
    "file": "quenelle-lyonnaise.jpg"
  },
  {
    "name": "Corniotte de Louhans",
    "file": "corniotte-de-louhans.jpg"
  },
  {
    "name": "Comté",
    "file": "comte.jpg"
  },
  {
    "name": "Mont d'Or",
    "file": "mont-d-or.jpg"
  },
  {
    "name": "Morbier",
    "file": "morbier.jpg"
  },
  {
    "name": "Époisses",
    "file": "epoisses.jpg"
  },
  {
    "name": "Mâconnais",
    "file": "maconnais.jpg"
  },
  {
    "name": "Nougat de Montélimar",
    "file": "nougat-de-montelimar.jpg"
  },
  {
    "name": "Lentille verte du Puy",
    "file": "lentille-verte-du-puy.jpg"
  },
  {
    "name": "Pastilles de Vichy",
    "file": "pastilles-de-vichy.jpg"
  },
  {
    "name": "Marrons glacés de Privas",
    "file": "marrons-glaces-de-privas.jpg"
  },
  {
    "name": "Crème de marrons d'Ardèche",
    "file": "creme-de-marrons-dardeche.jpg"
  },
  {
    "name": "Lunettes de Romans",
    "file": "lunettes-de-romans.jpg"
  },
  {
    "name": "Pompes aux grattons",
    "file": "pompes-aux-grattons.jpg"
  },
  {
    "name": "Râpée stéphanoise",
    "file": "rapee-stephanoise.jpg"
  },
  {
    "name": "Noix de Grenoble",
    "file": "noix-de-grenoble.jpg"
  },
  {
    "name": "Gâteau de Savoie",
    "file": "gateau-de-savoie.jpg"
  },
  {
    "name": "Crozets de Savoie",
    "file": "crozets-de-savoie.jpg"
  },
  {
    "name": "Cantal",
    "file": "cantal.jpg"
  },
  {
    "name": "Salers",
    "file": "salers.jpg"
  },
  {
    "name": "Bleu d'Auvergne",
    "file": "bleu-d-auvergne.jpg"
  },
  {
    "name": "Fourme d'Ambert",
    "file": "fourme-d-ambert.jpg"
  },
  {
    "name": "Saint-Nectaire",
    "file": "saint-nectaire.jpg"
  },
  {
    "name": "Reblochon",
    "file": "reblochon.jpg"
  },
  {
    "name": "Picodon",
    "file": "picodon.jpg"
  },
  {
    "name": "Rigotte de Condrieu",
    "file": "rigotte-de-condrieu.jpg"
  },
  {
    "name": "Beaufort",
    "file": "beaufort.jpg"
  },
  {
    "name": "Chevrotin",
    "file": "chevrotin.jpg"
  },
  {
    "name": "Tomme des Bauges",
    "file": "tomme-des-bauges.jpg"
  },
  {
    "name": "Coquelicot de Nemours",
    "file": "coquelicot-de-nemours.jpg"
  },
  {
    "name": "Financier",
    "file": "financier.jpg"
  },
  {
    "name": "Brie de Meaux",
    "file": "brie-de-meaux.jpg"
  },
  {
    "name": "Rigolette nantaise",
    "file": "rigolette-nantaise.jpg"
  },
  {
    "name": "Gâche vendéenne",
    "file": "gache-vendeenne.jpg"
  },
  {
    "name": "Mogette de Vendée",
    "file": "mogette-de-vendee.jpg"
  },
  {
    "name": "Rillettes du Mans",
    "file": "rillettes-du-mans.jpg"
  },
  {
    "name": "Rillettes de Tours",
    "file": "rillettes-de-tours.jpg"
  },
  {
    "name": "Tarte tatin",
    "file": "tarte-tatin.jpg"
  },
  {
    "name": "Vinaigre d'Orléans",
    "file": "vinaigre-dorleans.jpg"
  },
  {
    "name": "Safran du Gâtinais",
    "file": "safran-du-gatinais.jpg"
  },
  {
    "name": "Sainte-Maure de Touraine",
    "file": "sainte-maure-de-touraine.jpg"
  },
  {
    "name": "Selles-sur-Cher",
    "file": "selles-sur-cher.jpg"
  },
  {
    "name": "Valençay",
    "file": "valencay.jpg"
  },
  {
    "name": "Pouligny-Saint-Pierre",
    "file": "pouligny-saint-pierre.jpg"
  },
  {
    "name": "Fromage d'Olivet",
    "file": "fromage-d-olivet.jpg"
  },
  {
    "name": "Trèfle du Perche",
    "file": "trefle-du-perche.jpg"
  },
  {
    "name": "Canistrelli corse",
    "file": "canistrelli-corse.jpg"
  },
  {
    "name": "Figatellu",
    "file": "figatellu.jpg"
  },
  {
    "name": "Brocciu",
    "file": "brocciu.jpg"
  },
  {
    "name": "Gâteau creusois",
    "file": "gateau-creusois.jpg"
  },
  {
    "name": "Chabichou du Poitou",
    "file": "chabichou-du-poitou.jpg"
  },
  {
    "name": "Ossau-Iraty",
    "file": "ossau-iraty.jpg"
  },
  {
    "name": "Bergamote de Nancy",
    "file": "bergamote-de-nancy.jpg"
  },
  {
    "name": "Berlingot de Cauterets",
    "file": "berlingot-de-cauterets.jpg"
  },
  {
    "name": "Berlingot nantais",
    "file": "berlingot-nantais.jpg"
  },
  {
    "name": "Dragée de Verdun",
    "file": "dragee-de-verdun.jpg"
  },
  {
    "name": "Négus de Nevers",
    "file": "negus-de-nevers.jpg"
  },
  {
    "name": "Forestine de Bourges",
    "file": "forestine-de-bourges.jpg"
  },
  {
    "name": "Praline de Montargis",
    "file": "praline-de-montargis.jpg"
  },
  {
    "name": "Cotignac d'Orléans",
    "file": "cotignac-d-orleans.jpg"
  },
  {
    "name": "Sucre d'orge des Religieuses de Moret",
    "file": "sucre-d-orge-des-religieuses-de-moret.jpg"
  },
  {
    "name": "Bonbon à la verveine du Velay",
    "file": "bonbon-a-la-verveine-du-velay.jpg"
  },
  {
    "name": "Sucre de pomme de Rouen",
    "file": "sucre-de-pomme-de-rouen.jpg"
  },
  {
    "name": "Cassissine de Dijon",
    "file": "cassissine-de-dijon.jpg"
  },
  {
    "name": "Angélique confite de Niort",
    "file": "angelique-confite-de-niort.jpg"
  },
  {
    "name": "Bouchon de Bordeaux",
    "file": "bouchon-de-bordeaux.jpg"
  },
  {
    "name": "Chique de Bavay",
    "file": "chique-de-bavay.jpg"
  },
  {
    "name": "Grisette de Montpellier",
    "file": "grisette-de-montpellier.jpg"
  },
  {
    "name": "Cédrat confit de Corse",
    "file": "cedrat-confit-de-corse.jpg"
  },
  {
    "name": "Nougat de Limoux",
    "file": "nougat-de-limoux.jpg"
  },
  {
    "name": "Touron catalan",
    "file": "touron-catalan.jpg"
  },
  {
    "name": "Niniche de Quiberon",
    "file": "niniche-de-quiberon.jpg"
  },
  {
    "name": "Cœur de Plougastel",
    "file": "cur-de-plougastel.jpg"
  },
  {
    "name": "Bonbon aux bourgeons de sapin des Vosges",
    "file": "bonbon-aux-bourgeons-de-sapin-des-vosges.jpg"
  },
  {
    "name": "Rosette de Lyon",
    "file": "rosette-de-lyon.jpg"
  },
  {
    "name": "Saucisse de Montbéliard",
    "file": "saucisse-de-montbeliard.jpg"
  },
  {
    "name": "Brési de Franche-Comté",
    "file": "bresi-de-franche-comte.jpg"
  },
  {
    "name": "Jambon de Luxeuil",
    "file": "jambon-de-luxeuil.jpg"
  },
  {
    "name": "Jambon des Ardennes",
    "file": "jambon-des-ardennes.jpg"
  },
  {
    "name": "Jambon sec d'Auvergne",
    "file": "jambon-sec-d-auvergne.jpg"
  },
  {
    "name": "Jambon noir de Bigorre",
    "file": "jambon-noir-de-bigorre.jpg"
  },
  {
    "name": "Caillette ardéchoise",
    "file": "caillette-ardechoise.jpg"
  },
  {
    "name": "Coppa corse",
    "file": "coppa-corse.jpg"
  },
  {
    "name": "Lonzu corse",
    "file": "lonzu-corse.jpg"
  },
  {
    "name": "Prisuttu corse",
    "file": "prisuttu-corse.jpg"
  },
  {
    "name": "Panzetta corse",
    "file": "panzetta-corse.jpg"
  },
  {
    "name": "Andouille de Guéméné",
    "file": "andouille-de-guemene.jpg"
  },
  {
    "name": "Grenier médocain",
    "file": "grenier-medocain.jpg"
  },
  {
    "name": "Diot de Savoie",
    "file": "diot-de-savoie.jpg"
  },
  {
    "name": "Pâté de foie gras truffé du Périgord",
    "file": "pate-de-foie-gras-truffe-du-perigord.jpg"
  },
  {
    "name": "Confit de canard du Sud-Ouest",
    "file": "confit-de-canard-du-sud-ouest.jpg"
  },
  {
    "name": "Abondance",
    "file": "abondance.jpg"
  },
  {
    "name": "Bleu de Gex",
    "file": "bleu-de-gex.jpg"
  },
  {
    "name": "Bleu des Causses",
    "file": "bleu-des-causses.jpg"
  },
  {
    "name": "Bleu du Vercors-Sassenage",
    "file": "bleu-du-vercors-sassenage.jpg"
  },
  {
    "name": "Crottin de Chavignol",
    "file": "crottin-de-chavignol.jpg"
  },
  {
    "name": "Fourme de Montbrison",
    "file": "fourme-de-montbrison.jpg"
  },
  {
    "name": "Saint-Marcellin",
    "file": "saint-marcellin.jpg"
  },
  {
    "name": "Brillat-Savarin",
    "file": "brillat-savarin.jpg"
  },
  {
    "name": "Coulommiers",
    "file": "coulommiers.jpg"
  },
  {
    "name": "Brie de Melun",
    "file": "brie-de-melun.jpg"
  },
  {
    "name": "Tomme de Savoie",
    "file": "tomme-de-savoie.jpg"
  },
  {
    "name": "Cancoillotte",
    "file": "cancoillotte.jpg"
  },
  {
    "name": "Soumaintrain",
    "file": "soumaintrain.jpg"
  },
  {
    "name": "Boulette d'Avesnes",
    "file": "boulette-d-avesnes.jpg"
  },
  {
    "name": "Vieux-Lille",
    "file": "vieux-lille.jpg"
  },
  {
    "name": "Bethmale",
    "file": "bethmale.jpg"
  },
  {
    "name": "Gaperon",
    "file": "gaperon.jpg"
  },
  {
    "name": "Macaron de Nancy",
    "file": "macaron-de-nancy.jpg"
  },
  {
    "name": "Macaron de Saint-Émilion",
    "file": "macaron-de-saint-emilion.jpg"
  },
  {
    "name": "Nonnette de Dijon",
    "file": "nonnette-de-dijon.jpg"
  },
  {
    "name": "Pain d'épices de Dijon",
    "file": "pain-d-epices-de-dijon.jpg"
  },
  {
    "name": "Bredele alsacien",
    "file": "bredele-alsacien.jpg"
  },
  {
    "name": "Croquet de Saint-Mihiel",
    "file": "croquet-de-saint-mihiel.jpg"
  },
  {
    "name": "Gimblette d'Albi",
    "file": "gimblette-d-albi.jpg"
  },
  {
    "name": "Spéculoos du Nord",
    "file": "speculoos-du-nord.jpg"
  },
  {
    "name": "Crêpe dentelle de Quimper",
    "file": "crepe-dentelle-de-quimper.jpg"
  },
  {
    "name": "Quatre-quarts breton",
    "file": "quatre-quarts-breton.jpg"
  },
  {
    "name": "Pogne de Romans",
    "file": "pogne-de-romans.jpg"
  },
  {
    "name": "Gâteau basque",
    "file": "gateau-basque.jpg"
  },
  {
    "name": "Moutarde de Meaux",
    "file": "moutarde-de-meaux.jpg"
  },
  {
    "name": "Moutarde de Charroux",
    "file": "moutarde-de-charroux.jpg"
  },
  {
    "name": "Moutarde violette de Brive",
    "file": "moutarde-violette-de-brive.jpg"
  },
  {
    "name": "Vinaigre de Banyuls",
    "file": "vinaigre-de-banyuls.jpg"
  },
  {
    "name": "Huile d'olive de Nyons",
    "file": "huile-d-olive-de-nyons.jpg"
  },
  {
    "name": "Huile d'olive de Haute-Provence",
    "file": "huile-d-olive-de-haute-provence.jpg"
  },
  {
    "name": "Huile d'olive des Baux-de-Provence",
    "file": "huile-d-olive-des-baux-de-provence.jpg"
  },
  {
    "name": "Huile d'olive de Corse",
    "file": "huile-d-olive-de-corse.jpg"
  },
  {
    "name": "Huile de noix du Périgord",
    "file": "huile-de-noix-du-perigord.jpg"
  },
  {
    "name": "Miel des Cévennes",
    "file": "miel-des-cevennes.jpg"
  },
  {
    "name": "Miel de sapin des Vosges",
    "file": "miel-de-sapin-des-vosges.jpg"
  },
  {
    "name": "Miel de Corse",
    "file": "miel-de-corse.jpg"
  },
  {
    "name": "Safran du Quercy",
    "file": "safran-du-quercy.jpg"
  },
  {
    "name": "Sel de Noirmoutier",
    "file": "sel-de-noirmoutier.jpg"
  },
  {
    "name": "Sel de Ré",
    "file": "sel-de-re.jpg"
  },
  {
    "name": "Sel de Salies-de-Béarn",
    "file": "sel-de-salies-de-bearn.jpg"
  },
  {
    "name": "Olives de Nyons",
    "file": "olives-de-nyons.jpg"
  },
  {
    "name": "Cornichon d'Appoigny",
    "file": "cornichon-d-appoigny.jpg"
  },
  {
    "name": "Haricot tarbais",
    "file": "haricot-tarbais.jpg"
  },
  {
    "name": "Farine de châtaigne corse",
    "file": "farine-de-chataigne-corse.jpg"
  },
  {
    "name": "Aligot de l'Aubrac",
    "file": "aligot-de-l-aubrac.jpg"
  },
  {
    "name": "Choucroute d'Alsace",
    "file": "choucroute-d-alsace.jpg"
  },
  {
    "name": "Thon de Concarneau",
    "file": "thon-de-concarneau.jpg"
  },
  {
    "name": "Maquereau au vin blanc",
    "file": "maquereau-au-vin-blanc.jpg"
  },
  {
    "name": "Boutargue de Martigues",
    "file": "boutargue-de-martigues.jpg"
  },
  {
    "name": "Brandade de morue de Nîmes",
    "file": "brandade-de-morue-de-nimes.jpg"
  },
  {
    "name": "Soupe de poissons de Marseille",
    "file": "soupe-de-poissons-de-marseille.jpg"
  },
  {
    "name": "Caviar d'Aquitaine",
    "file": "caviar-d-aquitaine.jpg"
  },
  {
    "name": "Huître de Marennes-Oléron",
    "file": "huitre-de-marennes-oleron.jpg"
  },
  {
    "name": "Huître d'Arcachon",
    "file": "huitre-d-arcachon.jpg"
  },
  {
    "name": "Tielle sétoise",
    "file": "tielle-setoise.jpg"
  },
  {
    "name": "Pastis de Marseille",
    "file": "pastis-de-marseille.jpg"
  },
  {
    "name": "Chartreuse",
    "file": "chartreuse.jpg"
  },
  {
    "name": "Génépi des Alpes",
    "file": "genepi-des-alpes.jpg"
  },
  {
    "name": "Crème de cassis de Dijon",
    "file": "creme-de-cassis-de-dijon.jpg"
  },
  {
    "name": "Ratafia de Champagne",
    "file": "ratafia-de-champagne.jpg"
  },
  {
    "name": "Marc de Champagne",
    "file": "marc-de-champagne.jpg"
  },
  {
    "name": "Pineau des Charentes",
    "file": "pineau-des-charentes.jpg"
  },
  {
    "name": "Floc de Gascogne",
    "file": "floc-de-gascogne.jpg"
  },
  {
    "name": "Eau-de-vie de poire Williams",
    "file": "eau-de-vie-de-poire-williams.jpg"
  },
  {
    "name": "Volaille de Bresse",
    "file": "volaille-de-bresse.jpg"
  },
  {
    "name": "Bœuf charolais",
    "file": "buf-charolais.jpg"
  },
  {
    "name": "Bœuf de Bazas",
    "file": "buf-de-bazas.jpg"
  },
  {
    "name": "Bœuf blond d'Aquitaine",
    "file": "buf-blond-d-aquitaine.jpg"
  },
  {
    "name": "Agneau de Pauillac",
    "file": "agneau-de-pauillac.jpg"
  },
  {
    "name": "Agneau de pré-salé du Mont-Saint-Michel",
    "file": "agneau-de-pre-sale-du-mont-saint-michel.jpg"
  },
  {
    "name": "Agneau de Sisteron",
    "file": "agneau-de-sisteron.jpg"
  },
  {
    "name": "Taureau de Camargue",
    "file": "taureau-de-camargue.jpg"
  },
  {
    "name": "Poulet jaune des Landes",
    "file": "poulet-jaune-des-landes.jpg"
  },
  {
    "name": "Poulet coucou de Rennes",
    "file": "poulet-coucou-de-rennes.jpg"
  },
  {
    "name": "Chapon de Janzé",
    "file": "chapon-de-janze.jpg"
  },
  {
    "name": "Bœuf parthenais",
    "file": "buf-parthenais.jpg"
  },
  {
    "name": "Veau sous la mère du Limousin",
    "file": "veau-sous-la-mere-du-limousin.jpg"
  },
  {
    "name": "Bœuf fin gras du Mézenc",
    "file": "buf-fin-gras-du-mezenc.jpg"
  },
  {
    "name": "Génisse Fleur d'Aubrac",
    "file": "genisse-fleur-d-aubrac.jpg"
  },
  {
    "name": "Agneau du Quercy",
    "file": "agneau-du-quercy.jpg"
  },
  {
    "name": "Porc noir gascon",
    "file": "porc-noir-gascon.jpg"
  },
  {
    "name": "Palombe des Landes",
    "file": "palombe-des-landes.jpg"
  },
  {
    "name": "Bœuf bourguignon",
    "file": "buf-bourguignon.jpg"
  },
  {
    "name": "Coq au vin",
    "file": "coq-au-vin.jpg"
  },
  {
    "name": "Œufs en meurette",
    "file": "ufs-en-meurette.jpg"
  },
  {
    "name": "Pochouse",
    "file": "pochouse.jpg"
  },
  {
    "name": "Jambon persillé de Bourgogne",
    "file": "jambon-persille-de-bourgogne.jpg"
  },
  {
    "name": "Potée bourguignonne",
    "file": "potee-bourguignonne.jpg"
  },
  {
    "name": "Garbure",
    "file": "garbure.jpg"
  },
  {
    "name": "Poule au pot Henri IV",
    "file": "poule-au-pot-henri-iv.jpg"
  },
  {
    "name": "Tourin à l'ail",
    "file": "tourin-a-l-ail.jpg"
  },
  {
    "name": "Daube provençale",
    "file": "daube-provencale.jpg"
  },
  {
    "name": "Bouillabaisse",
    "file": "bouillabaisse.jpg"
  },
  {
    "name": "Aïoli",
    "file": "aioli.jpg"
  },
  {
    "name": "Pieds et paquets",
    "file": "pieds-et-paquets.jpg"
  },
  {
    "name": "Soupe au pistou",
    "file": "soupe-au-pistou.jpg"
  },
  {
    "name": "Salade niçoise",
    "file": "salade-nicoise.jpg"
  },
  {
    "name": "Pan bagnat",
    "file": "pan-bagnat.jpg"
  },
  {
    "name": "Pissaladière",
    "file": "pissaladiere.jpg"
  },
  {
    "name": "Socca",
    "file": "socca.jpg"
  },
  {
    "name": "Ratatouille",
    "file": "ratatouille.jpg"
  },
  {
    "name": "Tian provençal",
    "file": "tian-provencal.jpg"
  },
  {
    "name": "Bourride sétoise",
    "file": "bourride-setoise.jpg"
  },
  {
    "name": "Cargolade",
    "file": "cargolade.jpg"
  },
  {
    "name": "Boles de picolat",
    "file": "boles-de-picolat.jpg"
  },
  {
    "name": "Lièvre à la royale",
    "file": "lievre-a-la-royale.jpg"
  },
  {
    "name": "Embeurrée de chou",
    "file": "embeurree-de-chou.jpg"
  },
  {
    "name": "Chaudrée charentaise",
    "file": "chaudree-charentaise.jpg"
  },
  {
    "name": "Mouclade",
    "file": "mouclade.jpg"
  },
  {
    "name": "Éclade de moules",
    "file": "eclade-de-moules.jpg"
  },
  {
    "name": "Cagouilles à la charentaise",
    "file": "cagouilles-a-la-charentaise.jpg"
  },
  {
    "name": "Moules à la crème normande",
    "file": "moules-a-la-creme-normande.jpg"
  },
  {
    "name": "Escalope à la normande",
    "file": "escalope-a-la-normande.jpg"
  },
  {
    "name": "Marmite dieppoise",
    "file": "marmite-dieppoise.jpg"
  },
  {
    "name": "Canard à la rouennaise",
    "file": "canard-a-la-rouennaise.jpg"
  },
  {
    "name": "Carbonnade flamande",
    "file": "carbonnade-flamande.jpg"
  },
  {
    "name": "Potjevleesch",
    "file": "potjevleesch.jpg"
  },
  {
    "name": "Welsh",
    "file": "welsh.jpg"
  },
  {
    "name": "Hochepot",
    "file": "hochepot.jpg"
  },
  {
    "name": "Ficelle picarde",
    "file": "ficelle-picarde.jpg"
  },
  {
    "name": "Flamiche aux poireaux",
    "file": "flamiche-aux-poireaux.jpg"
  },
  {
    "name": "Tarte au Maroilles",
    "file": "tarte-au-maroilles.jpg"
  },
  {
    "name": "Anguille au vert",
    "file": "anguille-au-vert.jpg"
  },
  {
    "name": "Baeckeoffe",
    "file": "baeckeoffe.jpg"
  },
  {
    "name": "Flammekueche",
    "file": "flammekueche.jpg"
  },
  {
    "name": "Choucroute garnie",
    "file": "choucroute-garnie.jpg"
  },
  {
    "name": "Coq au Riesling",
    "file": "coq-au-riesling.jpg"
  },
  {
    "name": "Quiche lorraine",
    "file": "quiche-lorraine.jpg"
  },
  {
    "name": "Potée lorraine",
    "file": "potee-lorraine.jpg"
  },
  {
    "name": "Coq au vin jaune et morilles",
    "file": "coq-au-vin-jaune-et-morilles.jpg"
  },
  {
    "name": "Croûte aux morilles",
    "file": "croute-aux-morilles.jpg"
  },
  {
    "name": "Grenouilles à la comtoise",
    "file": "grenouilles-a-la-comtoise.jpg"
  },
  {
    "name": "Gaudes",
    "file": "gaudes.jpg"
  },
  {
    "name": "Gratin dauphinois",
    "file": "gratin-dauphinois.jpg"
  },
  {
    "name": "Gratin savoyard",
    "file": "gratin-savoyard.jpg"
  },
  {
    "name": "Fondue savoyarde",
    "file": "fondue-savoyarde.jpg"
  },
  {
    "name": "Tablier de sapeur",
    "file": "tablier-de-sapeur.jpg"
  },
  {
    "name": "Cervelle de canut",
    "file": "cervelle-de-canut.jpg"
  },
  {
    "name": "Tripous",
    "file": "tripous.jpg"
  },
  {
    "name": "Truffade",
    "file": "truffade.jpg"
  },
  {
    "name": "Chou farci auvergnat",
    "file": "chou-farci-auvergnat.jpg"
  },
  {
    "name": "Estofinado",
    "file": "estofinado.jpg"
  },
  {
    "name": "Pounti",
    "file": "pounti.jpg"
  },
  {
    "name": "Oignon de Roscoff",
    "file": "oignon-de-roscoff.jpg"
  },
  {
    "name": "Artichaut de Bretagne",
    "file": "artichaut-de-bretagne.jpg"
  },
  {
    "name": "Coco de Paimpol",
    "file": "coco-de-paimpol.jpg"
  },
  {
    "name": "Asperge des sables des Landes",
    "file": "asperge-des-sables-des-landes.jpg"
  },
  {
    "name": "Tomate de Marmande",
    "file": "tomate-de-marmande.jpg"
  },
  {
    "name": "Ail violet de Cadours",
    "file": "ail-violet-de-cadours.jpg"
  },
  {
    "name": "Ail blanc de Lomagne",
    "file": "ail-blanc-de-lomagne.jpg"
  },
  {
    "name": "Carotte des sables de Créances",
    "file": "carotte-des-sables-de-creances.jpg"
  },
  {
    "name": "Poireau de Créances",
    "file": "poireau-de-creances.jpg"
  },
  {
    "name": "Lentille verte du Berry",
    "file": "lentille-verte-du-berry.jpg"
  },
  {
    "name": "Mâche nantaise",
    "file": "mache-nantaise.jpg"
  },
  {
    "name": "Échalote d'Anjou",
    "file": "echalote-d-anjou.jpg"
  },
  {
    "name": "Melon du Quercy",
    "file": "melon-du-quercy.jpg"
  },
  {
    "name": "Melon de Cavaillon",
    "file": "melon-de-cavaillon.jpg"
  },
  {
    "name": "Fraise de Carpentras",
    "file": "fraise-de-carpentras.jpg"
  },
  {
    "name": "Fraise de Plougastel",
    "file": "fraise-de-plougastel.jpg"
  },
  {
    "name": "Châtaigne d'Ardèche",
    "file": "chataigne-d-ardeche.jpg"
  },
  {
    "name": "Pomme de terre de l'île de Ré",
    "file": "pomme-de-terre-de-l-ile-de-re.jpg"
  },
  {
    "name": "Lingot du Nord",
    "file": "lingot-du-nord.jpg"
  },
  {
    "name": "Endive du Nord",
    "file": "endive-du-nord.jpg"
  },
  {
    "name": "Fouée",
    "file": "fouee.jpg"
  },
  {
    "name": "Gâche normande",
    "file": "gache-normande.jpg"
  },
  {
    "name": "Brioche vendéenne",
    "file": "brioche-vendeenne.jpg"
  },
  {
    "name": "Cramique",
    "file": "cramique.jpg"
  },
  {
    "name": "Kouglof",
    "file": "kouglof.jpg"
  },
  {
    "name": "Pain plié",
    "file": "pain-plie.jpg"
  },
  {
    "name": "Pompe à l'huile",
    "file": "pompe-a-l-huile.jpg"
  },
  {
    "name": "Fougasse d'Aigues-Mortes",
    "file": "fougasse-d-aigues-mortes.jpg"
  },
  {
    "name": "Saucisse de Lacaune",
    "file": "saucisse-de-lacaune.jpg"
  },
  {
    "name": "Saucisson d'Arles",
    "file": "saucisson-d-arles.jpg"
  },
  {
    "name": "Andouille d'Aire-sur-la-Lys",
    "file": "andouille-d-aire-sur-la-lys.jpg"
  },
  {
    "name": "Boudin blanc de Rethel",
    "file": "boudin-blanc-de-rethel.jpg"
  },
  {
    "name": "Jambon de Paris",
    "file": "jambon-de-paris.jpg"
  },
  {
    "name": "Huître de Bouzigues",
    "file": "huitre-de-bouzigues.jpg"
  },
  {
    "name": "Coquille Saint-Jacques de Normandie",
    "file": "coquille-saint-jacques-de-normandie.jpg"
  },
  {
    "name": "Sardine de Saint-Gilles",
    "file": "sardine-de-saint-gilles.jpg"
  },
  {
    "name": "Coquillages de l'étang de Thau",
    "file": "coquillages-de-l-etang-de-thau.jpg"
  },
  {
    "name": "Homard à l'armoricaine",
    "file": "homard-a-l-armoricaine.jpg"
  },
  {
    "name": "Bleu de Termignon",
    "file": "bleu-de-termignon.jpg"
  },
  {
    "name": "Tomme des Pyrénées",
    "file": "tomme-des-pyrenees.jpg"
  },
  {
    "name": "Sucre d'orge de Vichy",
    "file": "sucre-d-orge-de-vichy.jpg"
  },
  {
    "name": "Gâteau battu picard",
    "file": "gateau-battu-picard.jpg"
  },
  {
    "name": "Tarte au sucre du Nord",
    "file": "tarte-au-sucre-du-nord.jpg"
  },
  {
    "name": "Macaron de Lusignan",
    "file": "macaron-de-lusignan.jpg"
  },
  {
    "name": "Pithiviers",
    "file": "pithiviers.jpg"
  },
  {
    "name": "Fiadone",
    "file": "fiadone.jpg"
  },
  {
    "name": "Castagnacciu",
    "file": "castagnacciu.jpg"
  },
  {
    "name": "Moutarde à la rose de Provins",
    "file": "moutarde-a-la-rose-de-provins.jpg"
  },
  {
    "name": "Huile d'olive de Nîmes",
    "file": "huile-d-olive-de-nimes.jpg"
  },
  {
    "name": "Olives de Lucques",
    "file": "olives-de-lucques.jpg"
  },
  {
    "name": "Vinaigre de cidre",
    "file": "vinaigre-de-cidre.jpg"
  },
  {
    "name": "Brousse du Rove",
    "file": "brousse-du-rove.jpg"
  },
  {
    "name": "Anchoïade",
    "file": "anchoiade.jpg"
  },
  {
    "name": "Petits farcis niçois",
    "file": "petits-farcis-nicois.jpg"
  },
  {
    "name": "Tourte de blettes niçoise",
    "file": "tourte-de-blettes-nicoise.jpg"
  },
  {
    "name": "Citron de Menton",
    "file": "citron-de-menton.jpg"
  },
  {
    "name": "Panisse",
    "file": "panisse.jpg"
  },
  {
    "name": "Estocaficada niçoise",
    "file": "estocaficada-nicoise.jpg"
  },
  {
    "name": "Artichaut à la barigoule",
    "file": "artichaut-a-la-barigoule.jpg"
  },
  {
    "name": "Gardiane de taureau",
    "file": "gardiane-de-taureau.jpg"
  },
  {
    "name": "Figue de Solliès",
    "file": "figue-de-sollies.jpg"
  },
  {
    "name": "Marron de Collobrières",
    "file": "marron-de-collobrieres.jpg"
  },
  {
    "name": "Nougat noir de Provence",
    "file": "nougat-noir-de-provence.jpg"
  },
  {
    "name": "Couronne des Rois",
    "file": "couronne-des-rois.jpg"
  },
  {
    "name": "Violette de Tourrettes-sur-Loup",
    "file": "violette-de-tourrettes-sur-loup.jpg"
  },
  {
    "name": "Pissalat",
    "file": "pissalat.jpg"
  },
  {
    "name": "Asperge de Lauris",
    "file": "asperge-de-lauris.jpg"
  },
  {
    "name": "Herbes de Provence",
    "file": "herbes-de-provence.jpg"
  },
  {
    "name": "Truffe noire du Vaucluse",
    "file": "truffe-noire-du-vaucluse.jpg"
  },
  {
    "name": "Lapin aux olives",
    "file": "lapin-aux-olives.jpg"
  },
  {
    "name": "Ravioli niçois",
    "file": "ravioli-nicois.jpg"
  },
  {
    "name": "Amande de Provence",
    "file": "amande-de-provence.jpg"
  },
  {
    "name": "Lamproie à la bordelaise",
    "file": "lamproie-a-la-bordelaise.jpg"
  },
  {
    "name": "Entrecôte à la bordelaise",
    "file": "entrecote-a-la-bordelaise.jpg"
  },
  {
    "name": "Cèpes à la bordelaise",
    "file": "cepes-a-la-bordelaise.jpg"
  },
  {
    "name": "Vinaigre de vin de Bordeaux",
    "file": "vinaigre-de-vin-de-bordeaux.jpg"
  },
  {
    "name": "Filet de bœuf sauce Périgueux",
    "file": "filet-de-buf-sauce-perigueux.jpg"
  },
  {
    "name": "Enchaud périgourdin",
    "file": "enchaud-perigourdin.jpg"
  },
  {
    "name": "Pommes de terre sarladaises",
    "file": "pommes-de-terre-sarladaises.jpg"
  },
  {
    "name": "Fraise du Périgord",
    "file": "fraise-du-perigord.jpg"
  },
  {
    "name": "Cabécou",
    "file": "cabecou.jpg"
  },
  {
    "name": "Châtaigne du Périgord",
    "file": "chataigne-du-perigord.jpg"
  },
  {
    "name": "Melon de Nérac",
    "file": "melon-de-nerac.jpg"
  },
  {
    "name": "Civet de lapin aux pruneaux",
    "file": "civet-de-lapin-aux-pruneaux.jpg"
  },
  {
    "name": "Croustade aux pommes",
    "file": "croustade-aux-pommes.jpg"
  },
  {
    "name": "Tourtière à l'armagnac",
    "file": "tourtiere-a-l-armagnac.jpg"
  },
  {
    "name": "Cou d'oie farci",
    "file": "cou-d-oie-farci.jpg"
  },
  {
    "name": "Dinde du Gers",
    "file": "dinde-du-gers.jpg"
  },
  {
    "name": "Madeleine de Dax",
    "file": "madeleine-de-dax.jpg"
  },
  {
    "name": "Saumon de l'Adour",
    "file": "saumon-de-l-adour.jpg"
  },
  {
    "name": "Chocolat de Bayonne",
    "file": "chocolat-de-bayonne.jpg"
  },
  {
    "name": "Cerise noire d'Itxassou",
    "file": "cerise-noire-d-itxassou.jpg"
  },
  {
    "name": "Porc basque Kintoa",
    "file": "porc-basque-kintoa.jpg"
  },
  {
    "name": "Ventrèche",
    "file": "ventreche.jpg"
  },
  {
    "name": "Poulet basquaise",
    "file": "poulet-basquaise.jpg"
  },
  {
    "name": "Pibales",
    "file": "pibales.jpg"
  },
  {
    "name": "Oignon doux des Cévennes",
    "file": "oignon-doux-des-cevennes.jpg"
  },
  {
    "name": "Châtaigne des Cévennes",
    "file": "chataigne-des-cevennes.jpg"
  },
  {
    "name": "Réglisse d'Uzès",
    "file": "reglisse-d-uzes.jpg"
  },
  {
    "name": "Pain de Beaucaire",
    "file": "pain-de-beaucaire.jpg"
  },
  {
    "name": "Navet noir de Pardailhan",
    "file": "navet-noir-de-pardailhan.jpg"
  },
  {
    "name": "Encornets farcis à la sétoise",
    "file": "encornets-farcis-a-la-setoise.jpg"
  },
  {
    "name": "Milhas",
    "file": "milhas.jpg"
  },
  {
    "name": "Pêche du Roussillon",
    "file": "peche-du-roussillon.jpg"
  },
  {
    "name": "Abricot rouge du Roussillon",
    "file": "abricot-rouge-du-roussillon.jpg"
  },
  {
    "name": "Artichaut violet du Roussillon",
    "file": "artichaut-violet-du-roussillon.jpg"
  },
  {
    "name": "Coque catalane",
    "file": "coque-catalane.jpg"
  },
  {
    "name": "Cerise de Céret",
    "file": "cerise-de-ceret.jpg"
  },
  {
    "name": "Coque quercynoise",
    "file": "coque-quercynoise.jpg"
  },
  {
    "name": "Noix du Quercy",
    "file": "noix-du-quercy.jpg"
  },
  {
    "name": "Chasselas de Moissac",
    "file": "chasselas-de-moissac.jpg"
  },
  {
    "name": "Gâteau à la broche",
    "file": "gateau-a-la-broche.jpg"
  },
  {
    "name": "Pomme de terre Béa du Roussillon",
    "file": "pomme-de-terre-bea-du-roussillon.jpg"
  },
  {
    "name": "Crème catalane",
    "file": "creme-catalane.jpg"
  },
  {
    "name": "Andouillette beaujolaise",
    "file": "andouillette-beaujolaise.jpg"
  },
  {
    "name": "Andouille de Charlieu",
    "file": "andouille-de-charlieu.jpg"
  },
  {
    "name": "Saucisson de Lyon",
    "file": "saucisson-de-lyon.jpg"
  },
  {
    "name": "Cervelas lyonnais",
    "file": "cervelas-lyonnais.jpg"
  },
  {
    "name": "Jésus de Lyon",
    "file": "jesus-de-lyon.jpg"
  },
  {
    "name": "Sabodet",
    "file": "sabodet.jpg"
  },
  {
    "name": "Grattons lyonnais",
    "file": "grattons-lyonnais.jpg"
  },
  {
    "name": "Boudin bressan",
    "file": "boudin-bressan.jpg"
  },
  {
    "name": "Boudin aux oignons",
    "file": "boudin-aux-oignons.jpg"
  },
  {
    "name": "Saucisson brioché",
    "file": "saucisson-brioche.jpg"
  },
  {
    "name": "Gâteau de foies blonds",
    "file": "gateau-de-foies-blonds.jpg"
  },
  {
    "name": "Poularde de Bresse demi-deuil",
    "file": "poularde-de-bresse-demi-deuil.jpg"
  },
  {
    "name": "Friture de Saône",
    "file": "friture-de-saone.jpg"
  },
  {
    "name": "Grenouilles de la Dombes",
    "file": "grenouilles-de-la-dombes.jpg"
  },
  {
    "name": "Écrevisses à la Nantua",
    "file": "ecrevisses-a-la-nantua.jpg"
  },
  {
    "name": "Poulet au vinaigre",
    "file": "poulet-au-vinaigre.jpg"
  },
  {
    "name": "Cardon lyonnais",
    "file": "cardon-lyonnais.jpg"
  },
  {
    "name": "Gras-double à la lyonnaise",
    "file": "gras-double-a-la-lyonnaise.jpg"
  },
  {
    "name": "Clapotons",
    "file": "clapotons.jpg"
  },
  {
    "name": "Salade lyonnaise",
    "file": "salade-lyonnaise.jpg"
  },
  {
    "name": "Gratinée lyonnaise",
    "file": "gratinee-lyonnaise.jpg"
  },
  {
    "name": "Fromage fort",
    "file": "fromage-fort.jpg"
  },
  {
    "name": "Ramequin du Bugey",
    "file": "ramequin-du-bugey.jpg"
  },
  {
    "name": "Galette bressane",
    "file": "galette-bressane.jpg"
  },
  {
    "name": "Bugnes lyonnaises",
    "file": "bugnes-lyonnaises.jpg"
  },
  {
    "name": "Cocon de Lyon",
    "file": "cocon-de-lyon.jpg"
  },
  {
    "name": "Papillote de Lyon",
    "file": "papillote-de-lyon.jpg"
  },
  {
    "name": "Carpe de la Dombes",
    "file": "carpe-de-la-dombes.jpg"
  },
  {
    "name": "Ravioles du Royans",
    "file": "ravioles-du-royans.jpg"
  },
  {
    "name": "Roulette du Bugey",
    "file": "roulette-du-bugey.jpg"
  },
  {
    "name": "Sablé aux noix du Bugey",
    "file": "sable-aux-noix-du-bugey.jpg"
  },
  {
    "name": "Ragoût de béatilles",
    "file": "ragout-de-beatilles.jpg"
  },
  {
    "name": "Boudin d'herbes",
    "file": "boudin-d-herbes.jpg"
  },
  {
    "name": "Bette d'Ampuis",
    "file": "bette-d-ampuis.jpg"
  },
  {
    "name": "Gratin de macaronis",
    "file": "gratin-de-macaronis.jpg"
  },
  {
    "name": "Brioche de Bourgoin",
    "file": "brioche-de-bourgoin.jpg"
  },
  {
    "name": "Omble chevalier",
    "file": "omble-chevalier.jpg"
  },
  {
    "name": "Féra du Léman",
    "file": "fera-du-leman.jpg"
  },
  {
    "name": "Lavaret du Bourget",
    "file": "lavaret-du-bourget.jpg"
  },
  {
    "name": "Atriau de Thonon",
    "file": "atriau-de-thonon.jpg"
  },
  {
    "name": "Pormonier",
    "file": "pormonier.jpg"
  },
  {
    "name": "Jambon de Savoie",
    "file": "jambon-de-savoie.jpg"
  },
  {
    "name": "Murson",
    "file": "murson.jpg"
  },
  {
    "name": "Emmental de Savoie",
    "file": "emmental-de-savoie.jpg"
  },
  {
    "name": "Tamié",
    "file": "tamie.jpg"
  },
  {
    "name": "Farçon savoyard",
    "file": "farcon-savoyard.jpg"
  },
  {
    "name": "Veau aux marrons",
    "file": "veau-aux-marrons.jpg"
  },
  {
    "name": "Matefaim",
    "file": "matefaim.jpg"
  },
  {
    "name": "Pomme de Savoie",
    "file": "pomme-de-savoie.jpg"
  },
  {
    "name": "Huile de noix du Dauphiné",
    "file": "huile-de-noix-du-dauphine.jpg"
  },
  {
    "name": "Rissole savoyarde",
    "file": "rissole-savoyarde.jpg"
  },
  {
    "name": "Bescoin",
    "file": "bescoin.jpg"
  },
  {
    "name": "Gâteau de Saint-Genix",
    "file": "gateau-de-saint-genix.jpg"
  },
  {
    "name": "Gâteau aux noix de Grenoble",
    "file": "gateau-aux-noix-de-grenoble.jpg"
  },
  {
    "name": "Pain de Modane",
    "file": "pain-de-modane.jpg"
  },
  {
    "name": "Pompe de l'Oisans",
    "file": "pompe-de-l-oisans.jpg"
  },
  {
    "name": "Noix de Grenoble fourrée",
    "file": "noix-de-grenoble-fourree.jpg"
  },
  {
    "name": "Chocolat à la chartreuse",
    "file": "chocolat-a-la-chartreuse.jpg"
  },
  {
    "name": "Truffe du Tricastin",
    "file": "truffe-du-tricastin.jpg"
  },
  {
    "name": "Pintadeau de la Drôme",
    "file": "pintadeau-de-la-drome.jpg"
  },
  {
    "name": "Agneau de la Drôme",
    "file": "agneau-de-la-drome.jpg"
  },
  {
    "name": "Ail de la Drôme",
    "file": "ail-de-la-drome.jpg"
  },
  {
    "name": "Tilleul des Baronnies",
    "file": "tilleul-des-baronnies.jpg"
  },
  {
    "name": "Suisse de Valence",
    "file": "suisse-de-valence.jpg"
  },
  {
    "name": "Pêche de l'Eyrieux",
    "file": "peche-de-l-eyrieux.jpg"
  },
  {
    "name": "Gâteau ardéchois aux marrons",
    "file": "gateau-ardechois-aux-marrons.jpg"
  },
  {
    "name": "Crique ardéchoise",
    "file": "crique-ardechoise.jpg"
  },
  {
    "name": "Ratte d'Ardèche",
    "file": "ratte-d-ardeche.jpg"
  },
  {
    "name": "Trappe de Chambarand",
    "file": "trappe-de-chambarand.jpg"
  },
  {
    "name": "Agneau pascal d'Annonay",
    "file": "agneau-pascal-d-annonay.jpg"
  },
  {
    "name": "Oignon de Tournon",
    "file": "oignon-de-tournon.jpg"
  },
  {
    "name": "Palet d'or de Moulins",
    "file": "palet-d-or-de-moulins.jpg"
  },
  {
    "name": "Pâté aux pommes de terre du Bourbonnais",
    "file": "pate-aux-pommes-de-terre-du-bourbonnais.jpg"
  },
  {
    "name": "Piquenchâgne",
    "file": "piquenchagne.jpg"
  },
  {
    "name": "Millard du Bourbonnais",
    "file": "millard-du-bourbonnais.jpg"
  },
  {
    "name": "Poulet fermier du Bourbonnais",
    "file": "poulet-fermier-du-bourbonnais.jpg"
  },
  {
    "name": "Agneau du Bourbonnais",
    "file": "agneau-du-bourbonnais.jpg"
  },
  {
    "name": "Crottes de marquis du Bourbonnais",
    "file": "crottes-de-marquis-du-bourbonnais.jpg"
  },
  {
    "name": "Gouère de Moulins",
    "file": "gouere-de-moulins.jpg"
  },
  {
    "name": "Brioche de Gannat",
    "file": "brioche-de-gannat.jpg"
  },
  {
    "name": "Praline d'Aigueperse",
    "file": "praline-d-aigueperse.jpg"
  },
  {
    "name": "Carottes Vichy",
    "file": "carottes-vichy.jpg"
  },
  {
    "name": "Omelette brayaude",
    "file": "omelette-brayaude.jpg"
  },
  {
    "name": "Coq au chanturgue",
    "file": "coq-au-chanturgue.jpg"
  },
  {
    "name": "Ail de Billom",
    "file": "ail-de-billom.jpg"
  },
  {
    "name": "Potée auvergnate",
    "file": "potee-auvergnate.jpg"
  },
  {
    "name": "Gigot brayaude",
    "file": "gigot-brayaude.jpg"
  },
  {
    "name": "Coufidou de bœuf",
    "file": "coufidou-de-buf.jpg"
  },
  {
    "name": "Bleu de Laqueuille",
    "file": "bleu-de-laqueuille.jpg"
  },
  {
    "name": "Flognarde",
    "file": "flognarde.jpg"
  },
  {
    "name": "Pompe aux pommes",
    "file": "pompe-aux-pommes.jpg"
  },
  {
    "name": "Tourte de seigle d'Auvergne",
    "file": "tourte-de-seigle-d-auvergne.jpg"
  },
  {
    "name": "Saucisson sec d'Auvergne",
    "file": "saucisson-sec-d-auvergne.jpg"
  },
  {
    "name": "Porc fermier d'Auvergne",
    "file": "porc-fermier-d-auvergne.jpg"
  },
  {
    "name": "Saucisse aux choux",
    "file": "saucisse-aux-choux.jpg"
  },
  {
    "name": "Croquant d'Auvergne",
    "file": "croquant-d-auvergne.jpg"
  },
  {
    "name": "Sanguette",
    "file": "sanguette.jpg"
  },
  {
    "name": "Bœuf de Salers",
    "file": "buf-de-salers.jpg"
  },
  {
    "name": "Boudin aux châtaignes",
    "file": "boudin-aux-chataignes.jpg"
  },
  {
    "name": "Cornet de Murat",
    "file": "cornet-de-murat.jpg"
  },
  {
    "name": "Falette",
    "file": "falette.jpg"
  },
  {
    "name": "Tome fraîche de l'Aubrac",
    "file": "tome-fraiche-de-l-aubrac.jpg"
  },
  {
    "name": "Sac d'os",
    "file": "sac-d-os.jpg"
  },
  {
    "name": "Mourtayrol",
    "file": "mourtayrol.jpg"
  },
  {
    "name": "Agneau noir du Velay",
    "file": "agneau-noir-du-velay.jpg"
  },
  {
    "name": "Petit salé aux lentilles",
    "file": "petit-sale-aux-lentilles.jpg"
  },
  {
    "name": "Saint-Florentin",
    "file": "saint-florentin.jpg"
  },
  {
    "name": "Cîteaux",
    "file": "citeaux.jpg"
  },
  {
    "name": "Charolais (fromage de chèvre)",
    "file": "charolais-fromage-de-chevre.jpg"
  },
  {
    "name": "Bouton de culotte",
    "file": "bouton-de-culotte.jpg"
  },
  {
    "name": "Jambon du Morvan",
    "file": "jambon-du-morvan.jpg"
  },
  {
    "name": "Andouillette de Chablis",
    "file": "andouillette-de-chablis.jpg"
  },
  {
    "name": "Andouillette de Clamecy",
    "file": "andouillette-de-clamecy.jpg"
  },
  {
    "name": "Judru de Chagny",
    "file": "judru-de-chagny.jpg"
  },
  {
    "name": "Coq au chambertin",
    "file": "coq-au-chambertin.jpg"
  },
  {
    "name": "Poulet Gaston Gérard",
    "file": "poulet-gaston-gerard.jpg"
  },
  {
    "name": "Saupiquet morvandiau",
    "file": "saupiquet-morvandiau.jpg"
  },
  {
    "name": "Crapiaux morvandiaux",
    "file": "crapiaux-morvandiaux.jpg"
  },
  {
    "name": "Tourte morvandelle",
    "file": "tourte-morvandelle.jpg"
  },
  {
    "name": "Cacou de Paray-le-Monial",
    "file": "cacou-de-paray-le-monial.jpg"
  },
  {
    "name": "Nougatine de Nevers",
    "file": "nougatine-de-nevers.jpg"
  },
  {
    "name": "Moutarde de Bourgogne",
    "file": "moutarde-de-bourgogne.jpg"
  },
  {
    "name": "Truffe de Bourgogne",
    "file": "truffe-de-bourgogne.jpg"
  },
  {
    "name": "Kir",
    "file": "kir.jpg"
  },
  {
    "name": "Biscuit de Chablis",
    "file": "biscuit-de-chablis.jpg"
  },
  {
    "name": "Tartouillat",
    "file": "tartouillat.jpg"
  },
  {
    "name": "Croquet du Bazois",
    "file": "croquet-du-bazois.jpg"
  },
  {
    "name": "Potée comtoise",
    "file": "potee-comtoise.jpg"
  },
  {
    "name": "Gratin de poireaux à la comtoise",
    "file": "gratin-de-poireaux-a-la-comtoise.jpg"
  },
  {
    "name": "Sèche comtoise",
    "file": "seche-comtoise.jpg"
  },
  {
    "name": "Pain d'épices de Vercel",
    "file": "pain-d-epices-de-vercel.jpg"
  },
  {
    "name": "Écrevisses au château-chalon",
    "file": "ecrevisses-au-chateau-chalon.jpg"
  },
  {
    "name": "Truite au vin rouge",
    "file": "truite-au-vin-rouge.jpg"
  },
  {
    "name": "Miel de sapin du Jura",
    "file": "miel-de-sapin-du-jura.jpg"
  },
  {
    "name": "Vin jaune du Jura",
    "file": "vin-jaune-du-jura.jpg"
  },
  {
    "name": "Macvin du Jura",
    "file": "macvin-du-jura.jpg"
  },
  {
    "name": "Escargots aux noisettes",
    "file": "escargots-aux-noisettes.jpg"
  },
  {
    "name": "Pâté lorrain",
    "file": "pate-lorrain.jpg"
  },
  {
    "name": "Tourte lorraine",
    "file": "tourte-lorraine.jpg"
  },
  {
    "name": "Baba au rhum",
    "file": "baba-au-rhum.jpg"
  },
  {
    "name": "Madeleine de Liverdun",
    "file": "madeleine-de-liverdun.jpg"
  },
  {
    "name": "Mirabelle de Lorraine",
    "file": "mirabelle-de-lorraine.jpg"
  },
  {
    "name": "Quetsche de Lorraine",
    "file": "quetsche-de-lorraine.jpg"
  },
  {
    "name": "Tarte aux mirabelles",
    "file": "tarte-aux-mirabelles.jpg"
  },
  {
    "name": "Confiture de groseilles de Bar-le-Duc",
    "file": "confiture-de-groseilles-de-bar-le-duc.jpg"
  },
  {
    "name": "Boulet de Metz",
    "file": "boulet-de-metz.jpg"
  },
  {
    "name": "Boudin noir de Nancy",
    "file": "boudin-noir-de-nancy.jpg"
  },
  {
    "name": "Jambon au foin",
    "file": "jambon-au-foin.jpg"
  },
  {
    "name": "Fraise de Woippy",
    "file": "fraise-de-woippy.jpg"
  },
  {
    "name": "Salade de pissenlits à la chaude meurotte",
    "file": "salade-de-pissenlits-a-la-chaude-meurotte.jpg"
  },
  {
    "name": "Carpe à la bière",
    "file": "carpe-a-la-biere.jpg"
  },
  {
    "name": "Coq au vin gris",
    "file": "coq-au-vin-gris.jpg"
  },
  {
    "name": "Andouille du Val d'Ajol",
    "file": "andouille-du-val-d-ajol.jpg"
  },
  {
    "name": "Toffailles",
    "file": "toffailles.jpg"
  },
  {
    "name": "Tarte aux brimbelles",
    "file": "tarte-aux-brimbelles.jpg"
  },
  {
    "name": "Nonnette de Remiremont",
    "file": "nonnette-de-remiremont.jpg"
  },
  {
    "name": "Râpés de pommes de terre",
    "file": "rapes-de-pommes-de-terre.jpg"
  },
  {
    "name": "Foie gras d'oie de Strasbourg",
    "file": "foie-gras-d-oie-de-strasbourg.jpg"
  },
  {
    "name": "Presskopf",
    "file": "presskopf.jpg"
  },
  {
    "name": "Schäufele",
    "file": "schaufele.jpg"
  },
  {
    "name": "Leberwurst",
    "file": "leberwurst.jpg"
  },
  {
    "name": "Fleischschnacka",
    "file": "fleischschnacka.jpg"
  },
  {
    "name": "Tarte à l'oignon",
    "file": "tarte-a-l-oignon.jpg"
  },
  {
    "name": "Carpe frite du Sundgau",
    "file": "carpe-frite-du-sundgau.jpg"
  },
  {
    "name": "Matelote à l'alsacienne",
    "file": "matelote-a-l-alsacienne.jpg"
  },
  {
    "name": "Salade de cervelas",
    "file": "salade-de-cervelas.jpg"
  },
  {
    "name": "Oie de la Saint-Martin",
    "file": "oie-de-la-saint-martin.jpg"
  },
  {
    "name": "Quenelle de foie",
    "file": "quenelle-de-foie.jpg"
  },
  {
    "name": "Bibeleskäs",
    "file": "bibeleskas.jpg"
  },
  {
    "name": "Tarte aux quetsches",
    "file": "tarte-aux-quetsches.jpg"
  },
  {
    "name": "Berewecke",
    "file": "berewecke.jpg"
  },
  {
    "name": "Streusel",
    "file": "streusel.jpg"
  },
  {
    "name": "Tarte au fromage blanc",
    "file": "tarte-au-fromage-blanc.jpg"
  },
  {
    "name": "Mendiant alsacien",
    "file": "mendiant-alsacien.jpg"
  },
  {
    "name": "Mannele",
    "file": "mannele.jpg"
  },
  {
    "name": "Lamala",
    "file": "lamala.jpg"
  },
  {
    "name": "Apfelkiechle",
    "file": "apfelkiechle.jpg"
  },
  {
    "name": "Crémant d'Alsace",
    "file": "cremant-d-alsace.jpg"
  },
  {
    "name": "Champagne",
    "file": "champagne.jpg"
  },
  {
    "name": "Pied de porc à la Sainte-Menehould",
    "file": "pied-de-porc-a-la-sainte-menehould.jpg"
  },
  {
    "name": "Massepain de Reims",
    "file": "massepain-de-reims.jpg"
  },
  {
    "name": "Croquignole de Reims",
    "file": "croquignole-de-reims.jpg"
  },
  {
    "name": "Cacasse à cul nu",
    "file": "cacasse-a-cul-nu.jpg"
  },
  {
    "name": "Salade ardennaise au lard",
    "file": "salade-ardennaise-au-lard.jpg"
  },
  {
    "name": "Galette au sucre",
    "file": "galette-au-sucre.jpg"
  },
  {
    "name": "Potée champenoise",
    "file": "potee-champenoise.jpg"
  },
  {
    "name": "Coq au Bouzy",
    "file": "coq-au-bouzy.jpg"
  },
  {
    "name": "Lentillon rosé de Champagne",
    "file": "lentillon-rose-de-champagne.jpg"
  },
  {
    "name": "Jambon de Reims",
    "file": "jambon-de-reims.jpg"
  },
  {
    "name": "Bouchon de Champagne",
    "file": "bouchon-de-champagne.jpg"
  },
  {
    "name": "Rocroi",
    "file": "rocroi.jpg"
  },
  {
    "name": "Moules-frites",
    "file": "moules-frites.jpg"
  },
  {
    "name": "Mimolette",
    "file": "mimolette.jpg"
  },
  {
    "name": "Mont des Cats",
    "file": "mont-des-cats.jpg"
  },
  {
    "name": "Bergues",
    "file": "bergues.jpg"
  },
  {
    "name": "Lucullus de Valenciennes",
    "file": "lucullus-de-valenciennes.jpg"
  },
  {
    "name": "Andouillette de Cambrai",
    "file": "andouillette-de-cambrai.jpg"
  },
  {
    "name": "Caudière étaploise",
    "file": "caudiere-etaploise.jpg"
  },
  {
    "name": "Maquereau à la boulonnaise",
    "file": "maquereau-a-la-boulonnaise.jpg"
  },
  {
    "name": "Lapin aux pruneaux à la flamande",
    "file": "lapin-aux-pruneaux-a-la-flamande.jpg"
  },
  {
    "name": "Hareng saur",
    "file": "hareng-saur.jpg"
  },
  {
    "name": "Crevette grise",
    "file": "crevette-grise.jpg"
  },
  {
    "name": "Volaille de Licques",
    "file": "volaille-de-licques.jpg"
  },
  {
    "name": "Chuque du Nord",
    "file": "chuque-du-nord.jpg"
  },
  {
    "name": "Babelutte",
    "file": "babelutte.jpg"
  },
  {
    "name": "Faluche",
    "file": "faluche.jpg"
  },
  {
    "name": "Craquelin du Boulonnais",
    "file": "craquelin-du-boulonnais.jpg"
  },
  {
    "name": "Ail fumé d'Arleux",
    "file": "ail-fume-d-arleux.jpg"
  },
  {
    "name": "Pomme de terre de Merville",
    "file": "pomme-de-terre-de-merville.jpg"
  },
  {
    "name": "Genièvre du Nord",
    "file": "genievre-du-nord.jpg"
  },
  {
    "name": "Bière de garde",
    "file": "biere-de-garde.jpg"
  },
  {
    "name": "Pâté de canard d'Amiens",
    "file": "pate-de-canard-d-amiens.jpg"
  },
  {
    "name": "Haricot de Soissons",
    "file": "haricot-de-soissons.jpg"
  },
  {
    "name": "Rollot",
    "file": "rollot.jpg"
  },
  {
    "name": "Salicorne de la baie de Somme",
    "file": "salicorne-de-la-baie-de-somme.jpg"
  },
  {
    "name": "Agneau de pré-salé de la baie de Somme",
    "file": "agneau-de-pre-sale-de-la-baie-de-somme.jpg"
  },
  {
    "name": "Caghuse",
    "file": "caghuse.jpg"
  },
  {
    "name": "Soupe des hortillonnages",
    "file": "soupe-des-hortillonnages.jpg"
  },
  {
    "name": "Légumes des hortillonnages d'Amiens",
    "file": "legumes-des-hortillonnages-d-amiens.jpg"
  },
  {
    "name": "Carotte des sables de la baie de Somme",
    "file": "carotte-des-sables-de-la-baie-de-somme.jpg"
  },
  {
    "name": "Bisteu",
    "file": "bisteu.jpg"
  },
  {
    "name": "Artichaut de Laon",
    "file": "artichaut-de-laon.jpg"
  },
  {
    "name": "Fruits rouges du Noyonnais",
    "file": "fruits-rouges-du-noyonnais.jpg"
  },
  {
    "name": "Demoiselles de Cherbourg à la nage",
    "file": "demoiselles-de-cherbourg-a-la-nage.jpg"
  },
  {
    "name": "Sole à la normande",
    "file": "sole-a-la-normande.jpg"
  },
  {
    "name": "Coquilles Saint-Jacques à la honfleuraise",
    "file": "coquilles-saint-jacques-a-la-honfleuraise.jpg"
  },
  {
    "name": "Matelote d'anguilles de Caudebec",
    "file": "matelote-d-anguilles-de-caudebec.jpg"
  },
  {
    "name": "Huître de Saint-Vaast-la-Hougue",
    "file": "huitre-de-saint-vaast-la-hougue.jpg"
  },
  {
    "name": "Moule de bouchot",
    "file": "moule-de-bouchot.jpg"
  },
  {
    "name": "Poulet Vallée d'Auge",
    "file": "poulet-vallee-d-auge.jpg"
  },
  {
    "name": "Salade cauchoise",
    "file": "salade-cauchoise.jpg"
  },
  {
    "name": "Omelette de la Mère Poulard",
    "file": "omelette-de-la-mere-poulard.jpg"
  },
  {
    "name": "Tripes de la Ferté-Macé",
    "file": "tripes-de-la-ferte-mace.jpg"
  },
  {
    "name": "Boudin noir de Mortagne",
    "file": "boudin-noir-de-mortagne.jpg"
  },
  {
    "name": "Andouillette de Rouen",
    "file": "andouillette-de-rouen.jpg"
  },
  {
    "name": "Petit-suisse",
    "file": "petit-suisse.jpg"
  },
  {
    "name": "Teurgoule",
    "file": "teurgoule.jpg"
  },
  {
    "name": "Tarte normande",
    "file": "tarte-normande.jpg"
  },
  {
    "name": "Bourdelot",
    "file": "bourdelot.jpg"
  },
  {
    "name": "Mirliton de Rouen",
    "file": "mirliton-de-rouen.jpg"
  },
  {
    "name": "Sablé normand",
    "file": "sable-normand.jpg"
  },
  {
    "name": "Pain brié",
    "file": "pain-brie.jpg"
  },
  {
    "name": "Fallue",
    "file": "fallue.jpg"
  },
  {
    "name": "Chique de Caen",
    "file": "chique-de-caen.jpg"
  },
  {
    "name": "Cidre de Normandie",
    "file": "cidre-de-normandie.jpg"
  },
  {
    "name": "Calvados",
    "file": "calvados.jpg"
  },
  {
    "name": "Pommeau de Normandie",
    "file": "pommeau-de-normandie.jpg"
  },
  {
    "name": "Poiré domfrontais",
    "file": "poire-domfrontais.jpg"
  },
  {
    "name": "Beurre d'Isigny",
    "file": "beurre-d-isigny.jpg"
  },
  {
    "name": "Crème d'Isigny",
    "file": "creme-d-isigny.jpg"
  },
  {
    "name": "Brioche du Vast",
    "file": "brioche-du-vast.jpg"
  },
  {
    "name": "Jambon fumé du Cotentin",
    "file": "jambon-fume-du-cotentin.jpg"
  },
  {
    "name": "Graisse normande",
    "file": "graisse-normande.jpg"
  },
  {
    "name": "Tarte aux pommes d'Yport",
    "file": "tarte-aux-pommes-d-yport.jpg"
  },
  {
    "name": "Pieds de mouton à la rouennaise",
    "file": "pieds-de-mouton-a-la-rouennaise.jpg"
  },
  {
    "name": "Bœuf de race normande",
    "file": "buf-de-race-normande.jpg"
  },
  {
    "name": "Brioche moulinoise du Perche",
    "file": "brioche-moulinoise-du-perche.jpg"
  },
  {
    "name": "Trou normand",
    "file": "trou-normand.jpg"
  },
  {
    "name": "Gelée de pomme",
    "file": "gelee-de-pomme.jpg"
  },
  {
    "name": "Poireau de Carentan",
    "file": "poireau-de-carentan.jpg"
  },
  {
    "name": "Boudin blanc havrais",
    "file": "boudin-blanc-havrais.jpg"
  },
  {
    "name": "Kig ha farz",
    "file": "kig-ha-farz.jpg"
  },
  {
    "name": "Galette-saucisse",
    "file": "galette-saucisse.jpg"
  },
  {
    "name": "Galette de sarrasin",
    "file": "galette-de-sarrasin.jpg"
  },
  {
    "name": "Cotriade",
    "file": "cotriade.jpg"
  },
  {
    "name": "Coquille Saint-Jacques de la baie de Saint-Brieuc",
    "file": "coquille-saint-jacques-de-la-baie-de-saint-brieuc.jpg"
  },
  {
    "name": "Huître de Cancale",
    "file": "huitre-de-cancale.jpg"
  },
  {
    "name": "Huître plate de Belon",
    "file": "huitre-plate-de-belon.jpg"
  },
  {
    "name": "Langoustine du Guilvinec",
    "file": "langoustine-du-guilvinec.jpg"
  },
  {
    "name": "Araignée de mer",
    "file": "araignee-de-mer.jpg"
  },
  {
    "name": "Pâté de campagne breton",
    "file": "pate-de-campagne-breton.jpg"
  },
  {
    "name": "Saucisse de Molène",
    "file": "saucisse-de-molene.jpg"
  },
  {
    "name": "Gâteau breton",
    "file": "gateau-breton.jpg"
  },
  {
    "name": "Craquelin de Saint-Malo",
    "file": "craquelin-de-saint-malo.jpg"
  },
  {
    "name": "Chou-fleur de Bretagne",
    "file": "chou-fleur-de-bretagne.jpg"
  },
  {
    "name": "Cidre de Cornouaille",
    "file": "cidre-de-cornouaille.jpg"
  },
  {
    "name": "Chouchen",
    "file": "chouchen.jpg"
  },
  {
    "name": "Lambig",
    "file": "lambig.jpg"
  },
  {
    "name": "Beurre demi-sel de Bretagne",
    "file": "beurre-demi-sel-de-bretagne.jpg"
  },
  {
    "name": "Algues de Bretagne",
    "file": "algues-de-bretagne.jpg"
  },
  {
    "name": "Fontainebleau",
    "file": "fontainebleau.jpg"
  },
  {
    "name": "Soupe à l'oignon gratinée",
    "file": "soupe-a-l-oignon-gratinee.jpg"
  },
  {
    "name": "Paris-Brest",
    "file": "paris-brest.jpg"
  },
  {
    "name": "Saint-Honoré",
    "file": "saint-honore.jpg"
  },
  {
    "name": "Opéra",
    "file": "opera.jpg"
  },
  {
    "name": "Flan parisien",
    "file": "flan-parisien.jpg"
  },
  {
    "name": "Religieuse",
    "file": "religieuse.jpg"
  },
  {
    "name": "Niflette de Provins",
    "file": "niflette-de-provins.jpg"
  },
  {
    "name": "Brioche de Nanterre",
    "file": "brioche-de-nanterre.jpg"
  },
  {
    "name": "Baguette parisienne",
    "file": "baguette-parisienne.jpg"
  },
  {
    "name": "Confit de pétales de rose de Provins",
    "file": "confit-de-petales-de-rose-de-provins.jpg"
  },
  {
    "name": "Miel du Gâtinais",
    "file": "miel-du-gatinais.jpg"
  },
  {
    "name": "Menthe poivrée de Milly-la-Forêt",
    "file": "menthe-poivree-de-milly-la-foret.jpg"
  },
  {
    "name": "Chasselas de Thomery",
    "file": "chasselas-de-thomery.jpg"
  },
  {
    "name": "Cresson de Méréville",
    "file": "cresson-de-mereville.jpg"
  },
  {
    "name": "Champignon de Paris",
    "file": "champignon-de-paris.jpg"
  },
  {
    "name": "Asperge d'Argenteuil",
    "file": "asperge-d-argenteuil.jpg"
  },
  {
    "name": "Pêche de Montreuil",
    "file": "peche-de-montreuil.jpg"
  },
  {
    "name": "Haricot chevrier d'Arpajon",
    "file": "haricot-chevrier-d-arpajon.jpg"
  },
  {
    "name": "Rillons de Tours",
    "file": "rillons-de-tours.jpg"
  },
  {
    "name": "Andouille de Jargeau",
    "file": "andouille-de-jargeau.jpg"
  },
  {
    "name": "Sandre au beurre blanc",
    "file": "sandre-au-beurre-blanc.jpg"
  },
  {
    "name": "Géline de Touraine",
    "file": "geline-de-touraine.jpg"
  },
  {
    "name": "Pâté de Pâques berrichon",
    "file": "pate-de-paques-berrichon.jpg"
  },
  {
    "name": "Poulet en barbouille",
    "file": "poulet-en-barbouille.jpg"
  },
  {
    "name": "Matelote d'anguilles de Loire",
    "file": "matelote-d-anguilles-de-loire.jpg"
  },
  {
    "name": "Sablé de Nançay",
    "file": "sable-de-nancay.jpg"
  },
  {
    "name": "Macaron de Cormery",
    "file": "macaron-de-cormery.jpg"
  },
  {
    "name": "Nougat de Tours",
    "file": "nougat-de-tours.jpg"
  },
  {
    "name": "Asperge de Sologne",
    "file": "asperge-de-sologne.jpg"
  },
  {
    "name": "Poire tapée de Rivarennes",
    "file": "poire-tapee-de-rivarennes.jpg"
  },
  {
    "name": "Vouvray",
    "file": "vouvray.jpg"
  },
  {
    "name": "Quernon d'ardoise",
    "file": "quernon-d-ardoise.jpg"
  },
  {
    "name": "Crémet d'Anjou",
    "file": "cremet-d-anjou.jpg"
  },
  {
    "name": "Pâté aux prunes",
    "file": "pate-aux-prunes.jpg"
  },
  {
    "name": "Cointreau",
    "file": "cointreau.jpg"
  },
  {
    "name": "Rillauds d'Anjou",
    "file": "rillauds-d-anjou.jpg"
  },
  {
    "name": "Coteaux du Layon",
    "file": "coteaux-du-layon.jpg"
  },
  {
    "name": "Beurre blanc nantais",
    "file": "beurre-blanc-nantais.jpg"
  },
  {
    "name": "Curé nantais",
    "file": "cure-nantais.jpg"
  },
  {
    "name": "Muscadet",
    "file": "muscadet.jpg"
  },
  {
    "name": "Gros plant du Pays nantais",
    "file": "gros-plant-du-pays-nantais.jpg"
  },
  {
    "name": "Gâteau nantais",
    "file": "gateau-nantais.jpg"
  },
  {
    "name": "Petit-beurre nantais",
    "file": "petit-beurre-nantais.jpg"
  },
  {
    "name": "Jambon de Vendée",
    "file": "jambon-de-vendee.jpg"
  },
  {
    "name": "Préfou",
    "file": "prefou.jpg"
  },
  {
    "name": "Fion vendéen",
    "file": "fion-vendeen.jpg"
  },
  {
    "name": "Canard de Challans",
    "file": "canard-de-challans.jpg"
  },
  {
    "name": "Bonnotte de Noirmoutier",
    "file": "bonnotte-de-noirmoutier.jpg"
  },
  {
    "name": "Poulet de Loué",
    "file": "poulet-de-loue.jpg"
  },
  {
    "name": "Marmite sarthoise",
    "file": "marmite-sarthoise.jpg"
  },
  {
    "name": "Fleur de sel de Guérande",
    "file": "fleur-de-sel-de-guerande.jpg"
  },
  {
    "name": "Cognac",
    "file": "cognac.jpg"
  },
  {
    "name": "Galette charentaise",
    "file": "galette-charentaise.jpg"
  },
  {
    "name": "Beurre Charentes-Poitou",
    "file": "beurre-charentes-poitou.jpg"
  },
  {
    "name": "Melon du Haut-Poitou",
    "file": "melon-du-haut-poitou.jpg"
  },
  {
    "name": "Jonchée",
    "file": "jonchee.jpg"
  },
  {
    "name": "Grillons charentais",
    "file": "grillons-charentais.jpg"
  },
  {
    "name": "Cornuelle",
    "file": "cornuelle.jpg"
  },
  {
    "name": "Clafoutis",
    "file": "clafoutis.jpg"
  },
  {
    "name": "Pâté de pommes de terre limousin",
    "file": "pate-de-pommes-de-terre-limousin.jpg"
  },
  {
    "name": "Porc cul noir du Limousin",
    "file": "porc-cul-noir-du-limousin.jpg"
  },
  {
    "name": "Madeleine de Saint-Yrieix",
    "file": "madeleine-de-saint-yrieix.jpg"
  },
  {
    "name": "Bœuf limousin",
    "file": "buf-limousin.jpg"
  },
  {
    "name": "Pomme du Limousin",
    "file": "pomme-du-limousin.jpg"
  },
  {
    "name": "Farcidure",
    "file": "farcidure.jpg"
  },
  {
    "name": "Salciccia corse",
    "file": "salciccia-corse.jpg"
  },
  {
    "name": "Sangui",
    "file": "sangui.jpg"
  },
  {
    "name": "Pâté de merle",
    "file": "pate-de-merle.jpg"
  },
  {
    "name": "Niolo",
    "file": "niolo.jpg"
  },
  {
    "name": "Bastelicaccia",
    "file": "bastelicaccia.jpg"
  },
  {
    "name": "Pulenda",
    "file": "pulenda.jpg"
  },
  {
    "name": "Aziminu",
    "file": "aziminu.jpg"
  },
  {
    "name": "Stufatu",
    "file": "stufatu.jpg"
  },
  {
    "name": "Cabri corse",
    "file": "cabri-corse.jpg"
  },
  {
    "name": "Storzapreti",
    "file": "storzapreti.jpg"
  },
  {
    "name": "Omelette au brocciu",
    "file": "omelette-au-brocciu.jpg"
  },
  {
    "name": "Cannelloni au brocciu",
    "file": "cannelloni-au-brocciu.jpg"
  },
  {
    "name": "Civet de sanglier à la myrte",
    "file": "civet-de-sanglier-a-la-myrte.jpg"
  },
  {
    "name": "Soupe corse",
    "file": "soupe-corse.jpg"
  },
  {
    "name": "Veau corse",
    "file": "veau-corse.jpg"
  },
  {
    "name": "Falculelle",
    "file": "falculelle.jpg"
  },
  {
    "name": "Frittelle au brocciu",
    "file": "frittelle-au-brocciu.jpg"
  },
  {
    "name": "Imbrucciata",
    "file": "imbrucciata.jpg"
  },
  {
    "name": "Migliacciu",
    "file": "migliacciu.jpg"
  },
  {
    "name": "Clémentine de Corse",
    "file": "clementine-de-corse.jpg"
  },
  {
    "name": "Châtaigne de Corse",
    "file": "chataigne-de-corse.jpg"
  },
  {
    "name": "Patrimonio",
    "file": "patrimonio.jpg"
  },
  {
    "name": "Muscat du Cap Corse",
    "file": "muscat-du-cap-corse.jpg"
  },
  {
    "name": "Liqueur de myrte",
    "file": "liqueur-de-myrte.jpg"
  },
  {
    "name": "Tarte tropézienne",
    "file": "tarte-tropezienne.jpg"
  },
  {
    "name": "Treize desserts de Noël",
    "file": "treize-desserts-de-noel.jpg"
  },
  {
    "name": "Oreillettes",
    "file": "oreillettes.jpg"
  },
  {
    "name": "Chichi fregi",
    "file": "chichi-fregi.jpg"
  },
  {
    "name": "Bohémienne",
    "file": "bohemienne.jpg"
  },
  {
    "name": "Tomme d'Arles",
    "file": "tomme-d-arles.jpg"
  },
  {
    "name": "Tellines de Camargue",
    "file": "tellines-de-camargue.jpg"
  },
  {
    "name": "Barbajuan",
    "file": "barbajuan.jpg"
  },
  {
    "name": "Pichade de Menton",
    "file": "pichade-de-menton.jpg"
  },
  {
    "name": "Châteauneuf-du-Pape",
    "file": "chateauneuf-du-pape.jpg"
  },
  {
    "name": "Bandol",
    "file": "bandol.jpg"
  },
  {
    "name": "Rosé de Provence",
    "file": "rose-de-provence.jpg"
  },
  {
    "name": "Rouille",
    "file": "rouille.jpg"
  },
  {
    "name": "Jambon de Bayonne",
    "file": "jambon-de-bayonne.jpg"
  },
  {
    "name": "Magret de canard",
    "file": "magret-de-canard.jpg"
  },
  {
    "name": "Grattons gascons",
    "file": "grattons-gascons.jpg"
  },
  {
    "name": "Axoa",
    "file": "axoa.jpg"
  },
  {
    "name": "Ttoro",
    "file": "ttoro.jpg"
  },
  {
    "name": "Salmis de palombe",
    "file": "salmis-de-palombe.jpg"
  },
  {
    "name": "Agneau de lait des Pyrénées",
    "file": "agneau-de-lait-des-pyrenees.jpg"
  },
  {
    "name": "Bœuf de Chalosse",
    "file": "buf-de-chalosse.jpg"
  },
  {
    "name": "Kiwi de l'Adour",
    "file": "kiwi-de-l-adour.jpg"
  },
  {
    "name": "Russe d'Oloron",
    "file": "russe-d-oloron.jpg"
  },
  {
    "name": "Coucougnette de Pau",
    "file": "coucougnette-de-pau.jpg"
  },
  {
    "name": "Macaron de Saint-Jean-de-Luz",
    "file": "macaron-de-saint-jean-de-luz.jpg"
  },
  {
    "name": "Béret basque",
    "file": "beret-basque.jpg"
  },
  {
    "name": "Merveilles",
    "file": "merveilles.jpg"
  },
  {
    "name": "Armagnac",
    "file": "armagnac.jpg"
  },
  {
    "name": "Izarra",
    "file": "izarra.jpg"
  },
  {
    "name": "Sauternes",
    "file": "sauternes.jpg"
  },
  {
    "name": "Jurançon",
    "file": "jurancon.jpg"
  },
  {
    "name": "Madiran",
    "file": "madiran.jpg"
  },
  {
    "name": "Saint-Émilion",
    "file": "saint-emilion.jpg"
  },
  {
    "name": "Petit pâté de Pézenas",
    "file": "petit-pate-de-pezenas.jpg"
  },
  {
    "name": "Pérail",
    "file": "perail.jpg"
  },
  {
    "name": "Bougnette du Tarn",
    "file": "bougnette-du-tarn.jpg"
  },
  {
    "name": "Flaune",
    "file": "flaune.jpg"
  },
  {
    "name": "Fouace aveyronnaise",
    "file": "fouace-aveyronnaise.jpg"
  },
  {
    "name": "Caladon de Nîmes",
    "file": "caladon-de-nimes.jpg"
  },
  {
    "name": "Croquant de Cordes",
    "file": "croquant-de-cordes.jpg"
  },
  {
    "name": "Croquant de Mende",
    "file": "croquant-de-mende.jpg"
  },
  {
    "name": "Fraise de Nîmes",
    "file": "fraise-de-nimes.jpg"
  },
  {
    "name": "Banyuls",
    "file": "banyuls.jpg"
  },
  {
    "name": "Maury",
    "file": "maury.jpg"
  },
  {
    "name": "Blanquette de Limoux",
    "file": "blanquette-de-limoux.jpg"
  },
  {
    "name": "Muscat de Frontignan",
    "file": "muscat-de-frontignan.jpg"
  },
  {
    "name": "Picpoul de Pinet",
    "file": "picpoul-de-pinet.jpg"
  }
]


def _get(url, params=None):
    for i,w in enumerate([0]+BACKOFF):
        if w: print(f"      (limite, pause {w}s)"); time.sleep(w)
        r=requests.get(url, params=params, headers=UA, timeout=45)
        if r.status_code==429: continue
        r.raise_for_status(); return r
    return None

def wiki_image(lang, query):
    """Image principale d'un article Wikipedia trouve par recherche."""
    r=_get(f"https://{lang}.wikipedia.org/w/api.php", {
        "action":"query","format":"json","generator":"search",
        "gsrsearch":query,"gsrlimit":"1","prop":"pageimages",
        "piprop":"original|thumbnail","pithumbsize":str(MAXPX)})
    if not r: return None
    pages=(r.json().get("query") or {}).get("pages") or {}
    for p in pages.values():
        th=p.get("thumbnail",{}).get("source")
        og=p.get("original",{}).get("source")
        url=th or og
        if url and not url.lower().endswith((".svg",".pdf")): return url
    return None

def commons_image(query):
    """Recherche directe d'un fichier sur Wikimedia Commons."""
    r=_get("https://commons.wikimedia.org/w/api.php", {
        "action":"query","format":"json","generator":"search",
        "gsrsearch":query,"gsrnamespace":"6","gsrlimit":"6",
        "prop":"imageinfo","iiprop":"url|mime","iiurlwidth":str(MAXPX)})
    if not r: return None
    pages=(r.json().get("query") or {}).get("pages") or {}
    for p in sorted(pages.values(), key=lambda x:x.get("index",999)):
        ii=(p.get("imageinfo") or [{}])[0]
        if ii.get("mime") in ("image/jpeg","image/png") and ii.get("thumburl"):
            return ii["thumburl"]
    return None

def variantes(nom):
    v=[nom]
    base=nom.split(" (")[0].strip()
    if base!=nom: v.append(base)
    for sep in [" de "," des "," du "," d'"]:
        if sep in nom:
            v.append(nom.split(sep)[0].strip()); break
    out=[]
    for x in v:
        if x and x not in out: out.append(x)
    return out

def trouver(nom):
    # 1) Wikipedia FR (nom + variantes)
    for q in variantes(nom):
        u=wiki_image("fr", q)
        if u: return u,"fr"
    # 2) Commons
    u=commons_image(nom)
    if u: return u,"commons"
    # 3) Wikipedia EN
    u=wiki_image("en", nom)
    if u: return u,"en"
    return None,None

def telecharger(url, chemin):
    r=_get(url)
    if not r: return False
    img=Image.open(io.BytesIO(r.content))
    if img.mode!="RGB": img=img.convert("RGB")
    img.thumbnail((MAXPX,MAXPX), Image.LANCZOS)
    img.save(chemin,"JPEG",quality=QUALITY,optimize=True)
    return True

def main():
    total=len(ITEMS); ok=sautes=0; echecs=[]
    src={"fr":0,"commons":0,"en":0}
    for i,it in enumerate(ITEMS,1):
        nom,fichier=it["name"],it["file"]
        pref=f"[{i:>3}/{total}] {nom}"
        if os.path.exists(fichier):
            sautes+=1; print(pref,"-> deja la"); continue
        try:
            url,source=trouver(nom)
            if not url:
                print(pref,"-> introuvable"); echecs.append(nom); time.sleep(PAUSE); continue
            if telecharger(url,fichier):
                src[source]+=1; ok+=1; print(pref,f"-> OK (via {source})")
            else:
                echecs.append(nom); print(pref,"-> echec telechargement")
        except Exception as e:
            echecs.append(nom); print(pref,f"-> ERREUR {e}")
        time.sleep(PAUSE)
    print("\n===== BILAN =====")
    print(f"Recuperees : {ok} (fr:{src['fr']} commons:{src['commons']} en:{src['en']}) | Deja presentes : {sautes} | Echecs : {len(echecs)}")
    if echecs:
        open("images_manquantes.txt","w",encoding="utf-8").write("\n".join(echecs))
        print("Introuvables notees dans images_manquantes.txt (envoie-la moi).")
    restantes=total-ok-sautes-len(echecs)
    if restantes>0: print(f"Il reste {restantes} a faire -> relance python3 images3.py.")
    else: print("Termine ! Uploade les .jpg sur GitHub.")

if __name__=="__main__": main()
