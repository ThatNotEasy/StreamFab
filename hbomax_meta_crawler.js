
function get_seasons_info(json_data, id) {
	var json_obj = JSON.parse(json_data)

	var season_num = 0;
	for (var i = 0; i < json_obj.length; i++) {
		var e_src = json_obj[i].body;

		if (e_src.seasonNumber !== undefined) {
			if (e_src.seasonNumber > season_num) {
				season_num = e_src.seasonNumber
			}
		}
		// 解决有些单 season 不能获取 tv 的问题
		// https://play.hbomax.com/page/urn:hbo:page:GVU2_3QlhmYNJjhsJAWUZ:type:series
		if (e_src.numberInSeries !== undefined) {
			season_num = 1
		}
	}

	src_seasons = new Array()
	for (var i = 0; i < season_num; i++) {
		obj = {
			"id": i + 1,
			"title": "Season " + String(i + 1),
			"release_time": "",
			"episodes": []
		}
		src_seasons.push(obj)
	}

	var all_episodes = new Array()
	for (var i = 0; i < json_obj.length; i++) {

		var e_src = json_obj[i].body;
		if (e_src.seasonNumber === undefined && e_src.numberInSeries === undefined) {
			continue
		}
		thumbs = e_src.images.tileburnedin
		if (thumbs.indexOf("&size") != -1) {
			thumbs = thumbs.split('&size')[0]
		}

		var e_des = {
			"seq": e_src.numberInSeason,
			"seasonNumber": e_src.seasonNumber,
			"episodeId": String(e_src.numberInSeason),
			"runtime": e_src.duration,
			"url": 'https://play.hbomax.com/episode/' + e_src.references.viewable,
			"synopsis": e_src.titles.full,
			"sortInt": e_src.numberInSeason + e_src.seasonNumber,
			"title": e_src.titles.full,
			"thumbs": {
				"url": thumbs
			}
		}
		if (e_src.numberInSeries !== undefined) {
			e_des['seasonNumber'] = 1
			e_des['seq'] = e_src.numberInSeries
			e_des['episodeId'] = e_src.numberInSeries
		}
		all_episodes.push(e_des)
	}


	var sort_all_episodes = all_episodes.sort(function (a, b) {
		return (a.sortInt - b.sortInt);
	})

	for (var i = 0; i < sort_all_episodes.length; i++) {
		e = sort_all_episodes[i]
		src_seasons[e.seasonNumber - 1].episodes.push(e)
	}

	var result = {
		"seasons": src_seasons
	}
	src_seasons_str = JSON.stringify(result)
	return src_seasons_str
}

function get_meta_info(json_data, id) {
	if (JSON.parse(json_data)[1].body.details === undefined) {
		json_obj = JSON.parse(json_data)[0]
		thumbs = json_obj.body.images.tileburnedin
		if (thumbs.indexOf("&size") != -1) {
			thumbs = thumbs.split('&size')[0]
		}

		all_obj = {
			"id": json_obj.id,
			"title": json_obj.body.titles.full,
			"runtime": json_obj.body.duration,
			"release_time": json_obj.body.releaseYear,
			"synopsis": json_obj.body.summaries.full,
			"thumbs": thumbs,
			"directors": [],
			"casts": [],
			"writers": [],
			"genres": [json_obj.body.ratingCode],
			"moodTags": []
		}
		return JSON.stringify(all_obj)
	} else {
		json_obj = JSON.parse(json_data)[1]
		thumbs = json_obj.body.details.image.uri
		if (thumbs.indexOf("&size") != -1) {
			thumbs = thumbs.split('&size')[0]
		}

		all_obj = {
			"id": id,
			"title": json_obj.body.details.title,
			"runtime": "",
			"release_time": "",
			"synopsis": json_obj.body.details.description,
			"thumbs": thumbs,
			"directors": [],
			"casts": [],
			"writers": [],
			"genres": [],
			"moodTags": []
		}
		return JSON.stringify(all_obj)
	}
}