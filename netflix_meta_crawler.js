function get_seasons_info(json_data, id) {
    let json_obj = JSON.parse(json_data)
    let seasons_src = json_obj.video.seasons
    let seasons_des = new Array()

    for (let index = 0; index < seasons_src.length; index++) {
        const s_src = seasons_src[index];
        let episodes_des = new Array()
        for (let j = 0; j < seasons_src[index].episodes.length; j++) {
            const e_src = seasons_src[index].episodes[j];
            let e_des = {
                "seq": e_src.seq,
                "episodeId": String(e_src.episodeId),
                "url": 'https://www.netflix.com/watch/' + String(e_src.episodeId),
                "synopsis": e_src.synopsis,
                "title": e_src.title,
				"runtime": e_src.runtime,
                "thumbs": {
                    "url": e_src.thumbs[0].url
                }
            }
            episodes_des.push(e_des)
        }
        let s_des = {
            "id": String(s_src.id),
            "release_time": String(s_src.year),
            "episodes": episodes_des,
            "seq": s_src.seq
        }

        seasons_des.push(s_des)
    }
    let all_obj = {
        "seasons": seasons_des
    }
    all_json = JSON.stringify(all_obj)
    return all_json
}

function get_meta_info(json_data, id) {

    let json_obj = JSON.parse(json_data)
    let video = json_obj.video
    let thumbs_url = video.artwork[0].url;
    let thumbs = {
        'url': thumbs_url
    }

    all_obj = {
        "id": video.currentEpisode,
		"type": video.type,
        "title": video.title,
        "runtime": video.runtime,
        "release_time": video.year,
        "synopsis": video.synopsis,
        "thumbs": thumbs,
        "directors": [],
        "casts": [],
        "writers": [],
        "genres": [video.rating],
        "moodTags": []
    }
    all_json = JSON.stringify(all_obj)
    return all_json
}