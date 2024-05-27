from flask import Flask, render_template, request, flash, redirect, session, url_for
import os
from werkzeug.utils import secure_filename
import sys
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
app = Flask(__name__)
app.secret_key = "kkkkk"

# Ensure the upload directory exists
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def process_image(filename):
    # Dummy image processing function for illustration
    return f"Processed {filename}"

@app.route("/")
def index():
    print("YES", file=sys.stderr)
    print("---------------", file=sys.stderr)
    return render_template("index.html")

@app.route("/greet", methods=["POST", "GET"])
def greet():
    flash("Hi " + str(request.form['name_input']) + ", great")
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(request.url)

    file = request.files['file']
    print(file, file=sys.stderr)

    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['filepath'] = filename  # Store the file path in the session
        print(f"Saved filepath in session: {filepath}", file=sys.stderr)
        print("---------------", file=sys.stderr)
        return redirect(url_for('results'))  # Redirect to the results page

    return render_template("index.html", button_text='No upload')

class_details = {
    'Clams': {
        'Desc': 'Clams are bivalve mollusks found in both freshwater and marine environments, characterized by their hard, hinged shells that consist of two symmetrical halves. These fascinating creatures play a crucial role in aquatic ecosystems, acting as natural filters by drawing in water and extracting plankton, algae, and other microscopic organisms for nourishment. This filtration process not only helps maintain water quality but also supports the broader food web. Clams have a muscular foot that allows them to burrow into the sediment, providing them with protection from predators such as starfish, birds, and humans. There are many species of clams, varying in size, shape, and habitat preferences. Some, like the giant clam, can reach impressive sizes and are found in coral reefs, while others, such as the soft-shell clam, inhabit sandy or muddy shores. Clams reproduce by releasing eggs and sperm into the water column, where fertilization occurs externally. The resulting larvae drift as plankton before settling on the seabed and developing into adult clams. In addition to their ecological importance, clams are highly valued as a food source worldwide. They can be consumed raw, steamed, boiled, baked, or fried, and are often included in dishes like clam chowder and paella. Clam harvesting can be done sustainably, but overfishing and habitat destruction pose significant threats to clam populations. Efforts to protect and restore clam habitats, along with responsible aquaculture practices, are essential for ensuring the continued availability of these vital and versatile mollusks.',
        'Life Expectancy': '20-30 years',
        'Diet': 'Filter feeders',
        'Rarity': 'Common',
        'Found in': 'Coastal waters',
        'Habitat': 'Benthic'
    },
    'Corals': {
        'Desc': 'Corals are remarkable marine invertebrates belonging to the phylum Cnidaria, which also includes jellyfish and sea anemones. They form large colonies composed of thousands of tiny, individual polyps, each with a cylindrical body topped by a mouth surrounded by tentacles. These polyps secrete calcium carbonate to create a hard, protective skeleton, which accumulates over time to form coral reefs. Coral reefs are among the most diverse and productive ecosystems on the planet, providing habitat and shelter for a vast array of marine species, including fish, invertebrates, and algae. Corals obtain much of their energy from a symbiotic relationship with microscopic algae called zooxanthellae, which live within their tissues. These algae photosynthesize, producing nutrients that corals use for growth and reproduction, while corals provide the algae with a protected environment and access to sunlight. This symbiosis is also responsible for the vibrant colors of many coral species. Corals can reproduce both sexually, by releasing eggs and sperm into the water, and asexually, through budding and fragmentation. Coral reefs face numerous threats, including climate change, ocean acidification, pollution, overfishing, and destructive fishing practices. Rising sea temperatures can cause coral bleaching, where corals expel their symbiotic algae, leading to a loss of color and, if prolonged, the death of the coral. Conservation efforts are crucial for the survival of coral reefs, including marine protected areas, sustainable fishing practices, and initiatives to reduce carbon emissions and pollution.',
        'Life Expectancy': 'Hundreds of years',
        'Diet': 'Photosynthetic zooxanthellae',
        'Rarity': 'Common in tropics',
        'Found in': 'Warm shallow waters',
        'Habitat': 'Reef-building'
    },
    'Crabs': {
        'Desc': 'Crabs are a diverse group of crustaceans found in various environments, from deep oceans to coastal shores, freshwater rivers, and even on land. They belong to the order Decapoda, which also includes lobsters, shrimp, and crayfish. Crabs have a broad, flattened body covered by a hard exoskeleton made of chitin, which they must periodically molt to grow. This process, known as ecdysis, allows them to shed their old shell and form a new, larger one.\nCrabs are easily recognized by their ten legs, with the front pair modified into powerful pincers or claws used for defense, feeding, and communication. These claws can vary greatly in size and shape, depending on the species and their specific ecological niche. Crabs are opportunistic feeders, consuming a wide range of food including algae, plankton, mollusks, small fish, and detritus. Some crabs are specialized hunters, while others are scavengers or even filter feeders.\nCrabs exhibit a wide range of behaviors and adaptations. For example, some species, like the blue crab, are excellent swimmers thanks to their paddle-shaped rear legs, while others, such as the hermit crab, use empty shells for protection. Crabs also engage in complex social behaviors, including territorial disputes, mating rituals, and communication through a variety of signals and postures. \nHuman activities, such as habitat destruction, pollution, and overfishing, pose significant threats to crab populations. Sustainable management practices and conservation efforts are essential to protect these fascinating and ecologically important creatures, ensuring their continued role in maintaining the health and balance of aquatic ecosystems.',
        'Life Expectancy': '3-30 years',
        'Diet': 'Omnivores, scavengers',
        'Rarity': 'Common',
        'Found in': 'Oceans, coastlines',
        'Habitat': 'Benthic, intertidal'
    },
    'Dolphin': {
        'Desc':'Dolphins are highly intelligent and social marine mammals belonging to the family Delphinidae. They are found in oceans and seas worldwide, with some species also inhabiting freshwater rivers. Dolphins are known for their streamlined bodies, exceptional swimming abilities, and playful behavior, often seen leaping out of the water, riding waves, and interacting with each other and humans. \n Dolphins possess a sophisticated echolocation system, which they use to navigate, hunt, and communicate. By emitting clicks and listening to the returning echoes, dolphins can determine the size, shape, and distance of objects, allowing them to locate prey and avoid obstacles in murky or dark waters. Their diet primarily consists of fish and squid, but some species also eat crustaceans and other marine organisms. Dolphins typically hunt in coordinated groups, known as pods, employing complex strategies to herd and capture their prey. \n Social structures in dolphin communities are complex and dynamic, with strong bonds forming between individuals. They communicate through a variety of vocalizations, including clicks, whistles, and body movements. These vocalizations are not only used for echolocation but also play a crucial role in social interactions, such as establishing dominance, coordinating group activities, and nurturing young.\n Dolphins are also known for their remarkable cognitive abilities, exhibiting problem-solving skills, self-awareness, and the capacity to learn and perform tasks. They are often studied for their intelligence and behavior, providing valuable insights into animal cognition and social structures. \nDespite their widespread distribution, dolphins face numerous threats from human activities, including habitat destruction, pollution, entanglement in fishing gear, and hunting. Conservation efforts, such as marine protected areas, regulations on fishing practices, and public awareness campaigns, are vital for protecting dolphin populations and ensuring their survival in the wild.',
        'Life Expectancy': '20-30 years',
        'Diet': 'Fish, squid',
        'Rarity': 'Common',
        'Found in': 'Oceans, coastal waters',
        'Habitat': 'Marine, migratory'
    },
    'Eel': {
        'Desc':'Eels are elongated, snake-like fish belonging to the order Anguilliformes, found in a variety of aquatic environments including freshwater rivers, coastal regions, and the deep sea. Characterized by their smooth, slimy bodies covered with tiny embedded scales, eels have dorsal and anal fins that merge with the tail fin, giving them a distinctive undulating movement. Many species, such as the American and European eels, are catadromous, migrating from freshwater habitats to the ocean to spawn. This remarkable journey, known as the eels life cycle, involves traveling thousands of miles to the Sargasso Sea, where they reproduce and die. \n Eels are nocturnal and secretive, often hiding in crevices or burrowing into the sand during the day. They are opportunistic feeders, consuming a varied diet that includes fish, crustaceans, and invertebrates. Their hunting strategy typically involves ambushing prey from their hiding spots. Despite their somewhat intimidating appearance, eels are an important part of the ecosystem, contributing to the balance of marine and freshwater habitats by controlling prey populations.\nEels have fascinated humans for centuries, both in folklore and as a delicacy in various cuisines. In Japan, grilled eel, or unagi, is a popular dish, while in Europe, eel is often smoked or jellied. However, overfishing, habitat loss, and barriers to migration, such as dams, have led to declines in eel populations, prompting conservation efforts to protect these mysterious and vital creatures.',
        'Life Expectancy': '5-60 years',
        'Diet': 'Carnivores, opportunistic',
        'Rarity': 'Common',
        'Found in': 'Oceans, coral reefs',
        'Habitat': 'Marine, reef-associated'
    },
    'Fish': {
        'Desc':'Fish are a diverse group of gill-bearing aquatic animals that constitute the superclass Pisces. They inhabit nearly every aquatic environment on Earth, from the deepest ocean trenches to high-altitude streams and lakes. Fish are characterized by their fins, scales, and streamlined bodies adapted for efficient swimming. They play critical roles in aquatic ecosystems as both predators and prey, maintaining the balance of marine and freshwater habitats.\nFish exhibit an astonishing variety of forms, behaviors, and adaptations. They range in size from the tiny Paedocypris, measuring just a few millimeters, to the massive whale shark, which can grow up to 40 feet long. Fish can be carnivorous, herbivorous, or omnivorous, with diets that include plankton, algae, other fish, and various invertebrates. Reproductive strategies among fish are equally diverse, encompassing everything from live-bearing species like guppies to egg-laying species like salmon, which undertake epic migrations to spawn in freshwater rivers.\nBeyond their ecological importance, fish are crucial to human economies and cultures around the world. They provide a primary source of protein for billions of people and support extensive fishing and aquaculture industries. Additionally, fish are popular in recreational fishing and as aquarium pets, bringing joy and fascination to enthusiasts globally.\nHowever, fish populations face significant threats from overfishing, habitat destruction, pollution, and climate change. Conservation efforts, sustainable fishing practices, and habitat restoration are essential to protect fish diversity and ensure the health of aquatic ecosystems for future generations.',
        'Life Expectancy': '5-10 years',
        'Diet': 'Algae, zooplankton',
        'Rarity': 'Common',
        'Found in': 'Coral Reefs',
        'Habitat': 'Tropical'
    },
    'Jelly Fish': {
        'Desc':'Jellyfish are gelatinous, free-swimming marine animals belonging to the phylum Cnidaria. They are found in oceans worldwide, from the surface to the deep sea, and are especially abundant in coastal waters. Jellyfish have a distinctive bell-shaped body, or medusa, with tentacles that hang down. These tentacles are equipped with specialized cells called cnidocytes, which contain nematocysts capable of delivering stings to capture prey and deter predators.\nDespite their simple structure, jellyfish exhibit a remarkable range of sizes and forms. Some, like the tiny Irukandji, are only a few centimeters in diameter, while others, like the lions mane jellyfish, can have tentacles extending over 100 feet. Jellyfish primarily feed on plankton, small fish, and other marine organisms, using their tentacles to ensnare and immobilize their prey. \n Jellyfish have a complex life cycle that includes both sexual and asexual reproduction. The medusa stage is the adult form, while the polyp stage is the larval form that attaches to the seabed and can produce new medusae through budding. This life cycle allows jellyfish to rapidly increase in number under favorable conditions, sometimes resulting in large blooms that can impact human activities such as fishing, tourism, and even power generation when they clog cooling intakes. \n Jellyfish play an important role in marine ecosystems, both as predators and prey. However, their populations can be affected by changes in ocean conditions, including warming waters and pollution. Understanding and managing jellyfish dynamics is crucial for maintaining healthy marine environments.',
        'Life Expectancy': '1-20 years',
        'Diet': 'Plankton, fish eggs',
        'Rarity': 'Common',
        'Found in': 'All oceans',
        'Habitat': 'Pelagic, drifters'
    },
    'Lobster': {
        'Desc':'Lobsters are large marine crustaceans belonging to the family Nephropidae, found in cold, rocky coastal waters around the world. Known for their hard exoskeleton, which they must periodically molt to grow, lobsters have long antennae and powerful claws. These claws, or chelae, are used for defense and capturing prey, with one typically being larger and adapted for crushing, while the other is more slender and suited for cutting. \nLobsters are primarily nocturnal and prefer to live in burrows or crevices in the seabed, where they are safe from predators and can ambush their prey. Their diet is diverse, including fish, mollusks, other crustaceans, and detritus. Lobsters are also known to exhibit cannibalistic behavior, particularly when food is scarce.\nReproduction in lobsters involves a complex mating ritual, after which the female carries the fertilized eggs under her abdomen until they hatch. The larvae are planktonic, drifting with the currents until they develop into juvenile lobsters and settle on the seabed. Lobsters can live for several decades, and some individuals have been known to reach impressive sizes, with the largest recorded lobster weighing over 44 pounds.\nLobsters are highly prized as a culinary delicacy, especially in regions such as New England and Atlantic Canada, where lobster fishing is a significant industry. They are typically prepared by boiling or steaming and are enjoyed for their sweet, tender meat. However, lobster populations are vulnerable to overfishing, habitat destruction, and climate change, making sustainable management practices essential to ensure their long-term survival and availability.',
        'Life Expectancy': '20-100 years',
        'Diet': 'Omnivores, scavengers',
        'Rarity': 'Common',
        'Found in': 'Coastal waters',
        'Habitat': 'Benthic, rocky'
    },
    'Nudibranchs': {
        'Desc':'Nudibranchs are a group of soft-bodied, marine gastropod mollusks known for their extraordinary colors and striking forms. Commonly referred to as sea slugs, nudibranchs are found in oceans worldwide, from shallow reefs to the deep sea. They are part of the subclass Opisthobranchia and are particularly noted for their lack of a protective shell in their adult stage.\n Nudibranchs exhibit a wide range of shapes, sizes, and colors, often serving as a warning to potential predators about their toxicity. They derive their vivid coloration from their diet, which includes sponges, hydroids, anemones, and other small marine organisms. Some nudibranchs are able to incorporate toxins or stinging cells from their prey into their own tissues as a defense mechanism, making them unpalatable or even dangerous to predators. \nThese fascinating creatures have a complex and varied reproductive system. They are hermaphroditic, meaning each individual possesses both male and female reproductive organs. When nudibranchs mate, they typically exchange sperm with one another, and both individuals can lay eggs. The eggs are often laid in intricate, ribbon-like coils on the substrate.\n Nudibranchs play an important role in marine ecosystems as both predators and prey. Their presence can indicate the health of the reef or marine environment they inhabit. Despite their delicate and often small stature, nudibranchs are resilient and have adapted to a wide range of marine conditions.\n Nudibranchs are popular among underwater photographers and marine biologists due to their striking appearance and ecological significance. However, like many marine species, they face threats from habitat destruction, climate change, and pollution. Protecting their habitats is crucial for maintaining the biodiversity and health of ocean ecosystems.',
        'Life Expectancy': '1-2 years',
        'Diet': 'Sponges, bryozoans',
        'Rarity': 'Uncommon',
        'Found in': 'Coral reefs, rocky',
        'Habitat': 'Benthic, shallow'
    },
    'Octopus': {
        'Desc':'Octopuses are highly intelligent and versatile marine animals belonging to the class Cephalopoda, which also includes squids and cuttlefish. They are characterized by their soft, bulbous bodies, large eyes, and eight long, flexible arms lined with suckers. Octopuses are found in various marine environments, from shallow coastal waters to the deep sea, and are renowned for their problem-solving abilities and complex behaviors. \nOne of the most fascinating aspects of octopus biology is their advanced nervous system and brain, which are among the largest and most complex of any invertebrate. This allows them to exhibit remarkable behaviors, such as using tools, navigating mazes, and escaping enclosures. Octopuses are also masters of camouflage, capable of changing their skin color and texture to blend seamlessly with their surroundings. This ability is facilitated by specialized skin cells called chromatophores, which can expand or contract to alter the animals appearance. \n Octopuses are carnivorous, feeding on a diet that includes crabs, shrimp, fish, and other mollusks. They use their arms to capture prey and their beak-like mouth to break through shells. Some species also produce venom to immobilize their prey. Reproduction involves a unique and often complex mating ritual, after which the female lays eggs and tends to them until they hatch. Unfortunately, octopuses have a relatively short lifespan, with many species living for just a few years.\nDespite their short lives, octopuses have a significant impact on their ecosystems as both predators and prey. They are also a subject of great interest in scientific research due to their intelligence and adaptability. Conservation efforts to protect marine habitats are essential to ensure the survival of these extraordinary creatures, which continue to captivate and inspire with their enigmatic and resourceful nature.',
        'Life Expectancy': '1-5 years',
        'Diet': 'Carnivores, crustaceans',
        'Rarity': 'Common',
        'Found in': 'All oceans',
        'Habitat': 'Benthic, coastal'
    },
    'Otter': {
        'Desc':'Otters are semi-aquatic mammals belonging to the family Mustelidae, which also includes weasels, badgers, and wolverines. There are 13 species of otters, and they are found in various habitats around the world, including rivers, lakes, coastal areas, and the open ocean. Otters are known for their playful behavior, sleek bodies, and thick, water-repellent fur that keeps them warm in cold water.\n Otters have a diet primarily composed of fish and invertebrates, but they are opportunistic feeders and may also consume amphibians, birds, and small mammals. They are skilled hunters, using their keen sense of sight, touch, and hearing to locate prey. Some species, such as the sea otter, use tools like rocks to break open hard-shelled prey, demonstrating remarkable problem-solving abilities.\n Otters are highly social animals, often seen in family groups or larger social groups. They communicate using a variety of vocalizations, scent markings, and body language. Their playful behavior, which includes sliding down mud or snow banks and engaging in mock fights, is thought to strengthen social bonds and develop hunting skills in younger otters. \nConservation efforts are critical for many otter species, which face threats from habitat destruction, pollution, and hunting for their valuable fur. Organizations around the world are working to protect otter habitats, enforce anti-poaching laws, and raise public awareness about the importance of these charismatic animals. By safeguarding otters and their environments, we help preserve the biodiversity and health of aquatic ecosystems.',
        'Life Expectancy': '8-10 years',
        'Diet': 'Fish, crustaceans',
        'Rarity': 'Uncommon',
        'Found in': 'Coastal waters',
        'Habitat': 'Marine, coastal'
    },
    'Penguin': {
        'Desc':'Penguins are flightless seabirds belonging to the family Spheniscidae, primarily found in the Southern Hemisphere, with a high concentration in Antarctica. Known for their distinctive black and white plumage and upright posture, penguins are adapted to life in the water, where they are agile and efficient swimmers. Their wings have evolved into flippers, enabling them to "fly" through the water with remarkable speed and agility.\nPenguins primarily feed on fish, squid, and krill, which they catch during their underwater foraging trips. They have excellent diving capabilities, with some species capable of reaching depths of over 500 meters. Penguins have a layer of blubber and densely packed feathers that provide insulation against the cold temperatures of their habitats. They also have a unique gland that allows them to excrete excess salt from their bodies, a crucial adaptation for living in marine environments.\nPenguins are social birds, often living in large colonies that can number in the thousands. These colonies provide protection against predators and harsh weather conditions. Penguins exhibit complex breeding behaviors, including elaborate courtship displays and the formation of strong pair bonds. Most species lay one or two eggs, with both parents sharing the responsibilities of incubation and chick-rearing.\nDespite their adaptations to harsh environments, penguins face numerous threats from climate change, overfishing, pollution, and habitat destruction. Melting ice and changing sea temperatures impact their food supply and breeding grounds, posing significant challenges to their survival. Conservation efforts are essential to protect these iconic birds and their habitats, ensuring that future generations can continue to marvel at their unique and captivating presence.',
        'Life Expectancy': '10-20 years',
        'Diet': 'Fish, krill',
        'Rarity': 'Common in Antarctica',
        'Found in': 'Antarctic, sub-Antarctic',
        'Habitat': 'Marine, coastal'
    },
    'Puffers': {
        'Desc':'Pufferfish, also known as blowfish, are a group of fish belonging to the family Tetraodontidae. They are renowned for their ability to inflate their bodies by swallowing water or air when threatened, transforming into a spiky, balloon-like shape that deters predators. This unique defense mechanism, combined with their often bright and intricate patterns, makes pufferfish one of the most fascinating and distinctive fish in the ocean.\nPufferfish are found in warm and temperate waters around the world, inhabiting coral reefs, mangroves, and coastal regions. They are primarily carnivorous, feeding on a diet of algae, invertebrates, and small fish. Pufferfish have strong, beak-like teeth that allow them to crush the shells of mollusks and crustaceans. Some species are also known to produce and harbor a potent neurotoxin called tetrodotoxin, which is highly poisonous to humans and predators alike.\nDespite their toxic nature, pufferfish are considered a delicacy in some cultures, particularly in Japan, where the fish, known as fugu, is carefully prepared by licensed chefs to avoid poisoning. This delicacy is prized for its delicate flavor and is a testament to the skill required to prepare it safely.\nPufferfish exhibit a variety of reproductive strategies, with some species laying eggs in nests built by males, while others release eggs and sperm into the water column for external fertilization. The larvae are planktonic, drifting with the currents until they develop into juvenile fish.\nPufferfish play an important role in marine ecosystems as both predators and prey. However, they face threats from habitat destruction, pollution, and overfishing. Conservation efforts aimed at protecting their habitats and regulating fishing practices are crucial to ensure the survival of pufferfish populations.',
        'Life Expectancy': '5-10 years',
        'Diet': 'Omnivores, algae',
        'Rarity': 'Common',
        'Found in': 'Tropical waters',
        'Habitat': 'Coral reefs'
    },
    'Sea Rays': {
        'Desc':'Stingrays are cartilaginous fish related to sharks, belonging to the order Myliobatiformes. They are characterized by their flattened bodies, wing-like pectoral fins, and long, slender tails, which often contain venomous barbs used for defense. Stingrays inhabit a variety of marine environments, including shallow coastal waters, coral reefs, and sandy or muddy bottoms, where they can easily blend in with the substrate.\nStingrays are bottom dwellers, spending much of their time partially buried in the sand. They feed on a diet of mollusks, crustaceans, and small fish, which they detect using electroreceptors located around their mouths. These electroreceptors allow stingrays to sense the electrical signals emitted by their prey, even when buried in the sand. Once located, stingrays use their powerful jaws to crush the shells of their prey.\nDespite their intimidating appearance and venomous barbs, stingrays are generally not aggressive and only use their stingers in self-defense when threatened or stepped on. They are known for their graceful swimming, often described as "flying" through the water by undulating their pectoral fins.\nStingrays play an important role in marine ecosystems as both predators and prey. They help control populations of benthic invertebrates and serve as a food source for larger predators, such as sharks. However, stingrays face threats from habitat destruction, pollution, and overfishing. Bycatch in commercial fisheries is also a significant concern, as stingrays are often unintentionally caught in nets.\nConservation efforts aimed at protecting marine habitats and reducing bycatch are essential to ensure the survival of stingray populations. These efforts include establishing marine protected areas, promoting sustainable fishing practices, and raising public awareness about the ecological importance of stingrays.',
        'Life Expectancy': '10-25 years',
        'Diet': 'Mollusks, crustaceans',
        'Rarity': 'Common',
        'Found in': 'Coastal waters',
        'Habitat': 'Benthic, sandy'
    },
    'Sea Urchins': {
        'Desc':'Sea urchins are spiny, globular marine animals belonging to the class Echinoidea. They are found in oceans worldwide, from shallow coastal waters to deep sea environments. Sea urchins have a hard, calcareous shell, or test, covered with movable spines that provide protection from predators and aid in locomotion. They also possess tube feet, which are used for movement, feeding, and respiration.\nSea urchins are herbivorous, feeding primarily on algae, which they graze using a specialized feeding structure called Aristotles lantern. This complex arrangement of muscles and teeth allows sea urchins to scrape and chew their food effectively. Some species are known to exhibit omnivorous behavior, consuming detritus and small invertebrates in addition to algae.\nSea urchins play a crucial role in maintaining the health of marine ecosystems, particularly coral reefs and kelp forests. By controlling algal growth, they prevent algae from overgrowing and smothering coral reefs or kelp beds. However, when sea urchin populations become too high, often due to the decline of their natural predators like sea otters, they can overgraze and cause significant damage to these ecosystems.\nReproduction in sea urchins involves the release of eggs and sperm into the water column, where external fertilization occurs. The resulting larvae are planktonic and undergo several developmental stages before settling on the seabed and transforming into juvenile sea urchins.\nSea urchins are also of economic importance, particularly in the food industry. The gonads, or roe, of certain species are considered a delicacy in many cultures, particularly in Japan, where they are known as uni. Sustainable harvesting practices are essential to ensure the long-term viability of sea urchin populations and the ecosystems they inhabit.',
        'Life Expectancy': '5-200 years',
        'Diet': 'Algae, plant matter',
        'Rarity': 'Common',
        'Found in': 'All oceans',
        'Habitat': 'Benthic, reef-associated'
    },
    'Seahorse': {
        'Desc':'Seahorses are small marine fish belonging to the genus Hippocampus, known for their distinctive horse-like head, prehensile tail, and upright swimming posture. They inhabit shallow coastal waters, estuaries, and coral reefs worldwide, where they are often found clinging to seagrasses, corals, and mangroves. Seahorses have a unique bony exoskeleton, which provides protection and support.\n One of the most fascinating aspects of seahorse biology is their reproductive strategy. Unlike most other fish, it is the male seahorse that becomes pregnant. During mating, the female transfers her eggs into a specialized brood pouch on the males abdomen, where they are fertilized and incubated until they hatch. The male then gives birth to fully formed, miniature seahorses, which are immediately independent.\nSeahorses are ambush predators, feeding primarily on small crustaceans and plankton. They use their elongated snouts to suck up prey, and their excellent camouflage abilities help them blend into their surroundings to avoid detection by predators and to surprise their prey. Seahorses have a prehensile tail, which they use to grasp onto seagrasses and corals, allowing them to remain stationary in the water.',
        'Life Expectancy': '1-5 years',
        'Diet': 'Plankton, small crustaceans',
        'Rarity': 'Common',
        'Found in': 'Coastal waters',
        'Habitat': 'Marine, seagrass beds'
    },
    'Seal': {
        'Desc':'Seals are marine mammals belonging to the family Phocidae, commonly referred to as "true seals." They are found in both polar and temperate regions, inhabiting coastal waters, ice floes, and sandy beaches. Seals are well-adapted to an aquatic lifestyle, with streamlined bodies, flipper-like limbs, and a thick layer of blubber that provides insulation and buoyancy.\nSeals are highly skilled swimmers, using their powerful hind flippers to propel themselves through the water with a side-to-side motion. They are also capable divers, able to hold their breath for extended periods and dive to great depths in search of food. Their diet consists primarily of fish, squid, and other marine invertebrates, which they catch using their sharp teeth and agile movements.',
        'Life Expectancy': '20-30 years',
        'Diet': 'Fish, crustaceans',
        'Rarity': 'Common',
        'Found in': 'Coastal waters',
        'Habitat': 'Marine, coastal'
    },
    'Sharks': {
        'Desc':'Sharks are a diverse group of cartilaginous fish belonging to the class Chondrichthyes. They are found in oceans worldwide, from shallow coastal waters to the deep sea. Sharks are known for their streamlined bodies, powerful tails, and multiple rows of sharp teeth, which they continuously replace throughout their lives. There are over 500 species of sharks, ranging from the small, bottom-dwelling dwarf lantern shark to the massive whale shark, the largest fish in the ocean.\nSharks are apex predators, playing a crucial role in maintaining the balance of marine ecosystems. They help regulate the populations of other marine species, ensuring the health and diversity of the ocean. Sharks exhibit a wide range of feeding behaviors and dietary preferences, from filter-feeding whale sharks that consume plankton to predatory great white sharks that hunt seals and other marine mammals.',
        'Life Expectancy': '20-30 years',
        'Diet': 'Carnivores',
        'Rarity': 'Common',
        'Found in': 'All oceans',
        'Habitat': 'Marine, coastal, pelagic'
    },
    'Shrimp': {
        'Desc':'Shrimp are small, slender-bodied crustaceans belonging to the order Decapoda. They are found in a wide range of aquatic environments, from freshwater rivers and lakes to the deep sea and coastal estuaries. Shrimp are characterized by their elongated bodies, long antennae, and numerous legs, which they use for swimming and burrowing.\nShrimp are omnivorous and feed on a variety of organic matter, including algae, plankton, detritus, and small invertebrates. Their feeding habits play an important role in the aquatic food web, helping to recycle nutrients and maintain ecosystem health. Shrimp are also prey for many larger animals, including fish, birds, and marine mammals.',
        'Life Expectancy': '1-7 years',
        'Diet': 'Detritivores, scavengers',
        'Rarity': 'Common',
        'Found in': 'All oceans',
        'Habitat': 'Benthic, reef-associated'
    },
    'Squid': {
        'Desc':'Squid are highly adaptable and fast-swimming marine cephalopods belonging to the order Teuthida. They are found in oceans worldwide, from the surface waters to the deep sea. Squid are known for their elongated bodies, large eyes, and eight arms, along with two longer tentacles used for capturing prey. Their streamlined shape and jet propulsion mechanism make them agile hunters and efficient swimmers.\nSquid are carnivorous, feeding primarily on fish, crustaceans, and other squid. They use their tentacles to grasp prey, drawing it toward their sharp, beak-like mouths. Squid have a complex nervous system and excellent vision, allowing them to detect and respond to changes in their environment with remarkable speed and precision.',
        'Life Expectancy': '1-5 years',
        'Diet': 'Carnivores, fish',
        'Rarity': 'Common',
        'Found in': 'All oceans',
        'Habitat': 'Pelagic, migratory'
    },
    'Starfish': {
        'Desc':'Starfish, also known as sea stars, are echinoderms belonging to the class Asteroidea. They are found in oceans worldwide, from the intertidal zone to the deep sea. Starfish are characterized by their radial symmetry, usually having five arms (though some species can have more), and a central disc. Their bodies are covered with a tough, spiny skin that provides protection from predators.\nStarfish play a vital role in marine ecosystems as both predators and scavengers. They primarily feed on bivalve mollusks, such as clams and oysters, by prying open the shells and extruding their stomachs to digest the soft tissues inside. Some species also consume detritus, algae, and other small marine organisms. This feeding behavior helps control bivalve populations and contributes to the health of the benthic community.',
        'Life Expectancy': '35 years',
        'Diet': 'Omnivores, scavengers',
        'Rarity': 'Common',
        'Found in': 'All oceans',
        'Habitat': 'Benthic, reef-associated'
    },
    'Turtle_Tortoise': {
        'Desc':'Sea turtles are large, marine reptiles belonging to the family Cheloniidae or Dermochelyidae. They are found in oceans around the world, from tropical to temperate waters. Sea turtles are known for their distinctive, streamlined shells, which provide protection and aid in hydrodynamics, allowing them to swim long distances. There are seven species of sea turtles, including the green, loggerhead, and leatherback turtles.\nSea turtles play a crucial role in marine ecosystems. They help maintain the health of seagrass beds and coral reefs, facilitate nutrient cycling, and support other marine life. For example, green turtles graze on seagrasses, which keeps the beds healthy and promotes growth. Leatherback turtles, on the other hand, consume large quantities of jellyfish, helping to regulate jellyfish populations.',
        'Life Expectancy': '50-100 years',
        'Diet': 'Omnivores, seagrass, jellyfish',
        'Rarity': 'Threatened/Endangered',
        'Found in': 'Tropical/subtropical oceans',
        'Habitat': 'Marine, migratory'
    },
    'Whale': {
        'Desc':'Whales are large marine mammals belonging to the order Cetacea, which also includes dolphins and porpoises. They are found in oceans worldwide, from polar to tropical waters. Whales are divided into two main groups: baleen whales (Mysticeti) and toothed whales (Odontoceti). Baleen whales, such as the blue whale and humpback whale, filter feed on small organisms like krill and plankton using baleen plates. Toothed whales, including sperm whales and orcas, have teeth and primarily feed on fish, squid, and other marine mammals.\nWhales play a significant role in marine ecosystems. They contribute to nutrient cycling by releasing fecal plumes that stimulate the growth of phytoplankton, a crucial component of the oceans food web. Their movements and behaviors, such as diving and feeding, also help mix ocean layers, promoting a healthy marine environment.',
        'Life Expectancy': '60-100 years',
        'Diet': 'Krill, small fish',
        'Rarity': 'Uncommon',
        'Found in': 'All oceans',
        'Habitat': 'Pelagic, migratory'
    }
}
@app.route("/results")
def results():
    filepath = session.get('filepath')  # Retrieve the file path from the session
    
    print(filepath, file=sys.stderr)

    rel_filepath = f"./static/uploads/{filepath}"

    print(rel_filepath, file=sys.stderr)
    class_name = classify_upload(rel_filepath)
    print(class_name, file=sys.stderr)
    if filepath:
        result = class_details.get(class_name, {})
        return render_template("results.html", class_name=class_name, result=result)
    else:
        return render_template("results.html")




def classify_upload(rel_filepath):
    def load_model(path):
        model = models.inception_v3(pretrained=True)
        num_classes = 23  # Replace with your actual number of classes
        num_ftrs = model.AuxLogits.fc.in_features
        model.AuxLogits.fc = nn.Linear(num_ftrs, num_classes)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
        model.load_state_dict(torch.load(path, map_location=device))
        model = model.to(device)
        model.eval()
        return model
    
    def process_image(image_path):
        image = Image.open(image_path).convert('RGB')
        transformations = transforms.Compose([
            transforms.Resize((299, 299)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        image_tensor = transformations(image).unsqueeze(0)  # Add batch dimension
        return image_tensor.to(device)


    def predict_image(model, image_tensor):
        with torch.no_grad():
            outputs = model(image_tensor)
            _, predicted = torch.max(outputs, 1)
            return predicted.item()  # Return the index of the predicted class
    image_path = rel_filepath

    model = load_model("Final_Model_FINAL.pth")
    image_tensor = process_image(image_path)
    class_index = predict_image(model, image_tensor)
    class_indices = {
        'Clams': 0, 'Corals': 1, 'Crabs': 2, 'Dolphin': 3, 'Eel': 4, 'Fish': 5, 'Jelly Fish': 6, 'Lobster': 7, 
        'Nudibranchs': 8, 'Octopus': 9, 'Otter': 10, 'Penguin': 11, 'Puffers': 12, 'Sea Rays': 13, 'Sea Urchins': 14, 
        'Seahorse': 15, 'Seal': 16, 'Sharks': 17, 'Shrimp': 18, 'Squid': 19, 'Starfish': 20, 'Turtle_Tortoise': 21, 
        'Whale': 22
    }
    predicted_class_label = list(class_indices.keys())[list(class_indices.values()).index(class_index)]

    print(predicted_class_label, file=sys.stderr)
    print("---------------", file=sys.stderr)
    
    return predicted_class_label

if __name__ == '__main__':
    app.run(debug=True)
