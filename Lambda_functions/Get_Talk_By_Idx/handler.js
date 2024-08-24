const mongoose = require('mongoose');
const connect_to_db = require('./db');
const Talk = require('./Talk'); // Modello per la collezione tedx_data
const WatchNext = require('./WatchNext'); // Modello per la collezione watch_next

// Mappatura dei tag con i loro valori
const tagValueMapping = {
    "society": 10,
    "politics": 9,
    "economics": 8,
    "health": 6,
    "sustainability": 8
};

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

        // Prepara la risposta
        const response = {
            _id: foundTalk._id,
            title: foundTalk.title,
            description: foundTalk.description,
            url: foundTalk.url,
            image_url: foundTalk.image_url,
            watch_next: []
        };

        // Trova i video correlati usando la collezione watch_next
        const watchNextData = await WatchNext.findOne({ video_id: body.idx });
        if (watchNextData) {
            
            console.log("WatchNext data found:", watchNextData);

            // Assicurati che related_videos_id_list contenga gli ID corretti
            console.log("Related video IDs:", watchNextData.related_videos_id_list);

            if (watchNextData.related_videos_id_list.length === 0) {
                console.log("related_videos_id_list is empty.");
            } else {
                
                // Usa gli ID come stringhe per la query
                const relatedVideoIds = watchNextData.related_videos_id_list;
                console.log("Using string IDs for query:", relatedVideoIds);

                // Verifica se gli ID nella query sono nel formato corretto
                const relatedVideos = await Talk.find({ '_id': { $in: relatedVideoIds } });
                console.log("Related videos found:", relatedVideos);
                
                // Calcola next_video_count per ciascun video correlato utilizzando i tag da watch_next
                const relatedVideosWithCount = await Promise.all(relatedVideos.map(async video => {
                    // Trova i tag dal record corrispondente in watch_next
                    const relatedVideoTagsData = await WatchNext.findOne({ video_id: video._id });
                    let relatedVideoCount = 0;
                    
                    if (relatedVideoTagsData && relatedVideoTagsData.tags) {
                        relatedVideoTagsData.tags.forEach(tag => {
                            if (tagValueMapping.hasOwnProperty(tag)) {
                                relatedVideoCount += tagValueMapping[tag];
            }
        });
    }

    return {
        _id: video._id,
        title: video.title,
        url: video.url,
        image_url: video.image_url,
        next_video_count: relatedVideoCount // Include il valore next_video_count
    };
}));

                
                // Ordina i video correlati in modo decrescente per next_video_count
                relatedVideosWithCount.sort((a, b) => b.next_video_count - a.next_video_count);

                // Aggiorna la risposta con i video correlati ordinati e con next_video_count incluso
                response.watch_next = relatedVideosWithCount.map(video => ({
                    _id: video._id,
                    title: video.title,
                    url: video.url,
                    image_url: video.image_url,
                    next_video_count: video.next_video_count // Includi next_video_count nell'array watch_next
                }));
            }
        } else {
            console.log("No WatchNext data found for video_id:", body.idx);
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


