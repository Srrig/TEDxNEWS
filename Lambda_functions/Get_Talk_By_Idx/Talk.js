const mongoose = require('mongoose');

// Definizione dello schema per la collezione tedx_data
const talkSchema = new mongoose.Schema({
    _id: String,           // ID univoco del talk
    slug: String,          // Slug del talk
    speakers: String,      // Relatori del talk
    title: String,         // Titolo del talk
    url: String,           // URL del talk
    description: String,   // Descrizione del talk
    duration: String,      // Durata del talk
    num_views: { type: Number, default: 0 }, // Numero di visualizzazioni     // Numero di visualizzazioni
    watch_next_s: [String] // Array di ID dei video suggeriti (watch next)
}, { collection: 'tedx_data' });

// Creazione e esportazione del modello
module.exports = mongoose.model('Talk', talkSchema);
