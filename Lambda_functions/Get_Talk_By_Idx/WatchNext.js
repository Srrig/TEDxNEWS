const mongoose = require('mongoose');

const watchNextSchema = new mongoose.Schema({
    video_id: String,                      // ID del video principale
    related_videos_id_list: [String],// Lista di ID dei video correlati
    image_url: String,
    url: String,
    tags: [String],                         // Array di tag associati al video
}, { collection: 'watch_next' });

module.exports = mongoose.model('WatchNext', watchNextSchema);
