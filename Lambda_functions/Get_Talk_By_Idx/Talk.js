const mongoose = require('mongoose');

// Definizione dello schema per la collezione tedx_data
const talkSchema = new mongoose.Schema({
    _id: String,           // ID univoco del talk
    slug: String,          // Slug del talk
    speakers: String,      // Relatori del talk
    title: String,         // Titolo del talk
    url: String,           // URL del talk
    description: String,   // Descrizione del talk
    image_url: String,     // URL dell'immagine
    duration: String,      // Durata del talk
    tags: [String],        // Array di tag associati al talk
}, { collection: 'tedx_data' });

// Creazione e esportazione del modello
module.exports = mongoose.model('Talk', talkSchema);
