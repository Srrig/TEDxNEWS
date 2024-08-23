const mongoose = require('mongoose');

const watchNextSchema = new mongoose.Schema({
    video_id: String,
    related_videos_id_list: [String]
}, { collection: 'watch_next' });

module.exports = mongoose.model('WatchNext', watchNextSchema);