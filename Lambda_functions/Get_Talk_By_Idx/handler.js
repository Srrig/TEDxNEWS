const mongoose = require('mongoose');
const connect_to_db = require('./db');
const Talk = require('./Talk'); // Modello per la collezione tedx_data
const WatchNext = require('./WatchNext'); // Modello per la collezione watch_next

module.exports.get_talk_by_id = async (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;

    let body = {};
    if (event.body) {
        body = JSON.parse(event.body);
    }

    if (!body.idx) {
        return callback(null, {
            statusCode: 500,
            headers: { 'Content-Type': 'text/plain' },
            body: 'Could not fetch the talk. idx is null.'
        });
    }

    try {
        await connect_to_db();

        // Trova il talk nella collezione tedx_data
        const foundTalk = await Talk.findById(body.idx);
        if (!foundTalk) {
            return callback(null, {
                statusCode: 404,
                headers: { 'Content-Type': 'text/plain' },
                body: 'Talk not found.'
            });
        }

        // Incrementa il numero di visualizzazioni
        foundTalk.num_views = (foundTalk.num_views || 0) + 1;
        await foundTalk.save();

        // Prepara la risposta
        const response = {
            _id: foundTalk._id,
            title: foundTalk.title,
            description: foundTalk.description,
            url: foundTalk.url,
            num_views: foundTalk.num_views,
            watch_next: []
        };

        // Trova i video correlati usando la collezione watch_next
        const watchNextData = await WatchNext.findOne({ video_id: body.idx });
        if (watchNextData) {
            response.watch_next = watchNextData.related_videos_id_list.map((video_id, index) => ({
                _id: video_id,
                title: watchNextData.title_related_videos_list[index]
            }));
        }

        return callback(null, {
            statusCode: 200,
            body: JSON.stringify(response)
        });
    } catch (err) {
        console.error('Error:', err);
        return callback(null, {
            statusCode: 500,
            headers: { 'Content-Type': 'text/plain' },
            body: 'An error occurred while processing your request.'
        });
    }
};