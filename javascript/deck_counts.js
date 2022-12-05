import * as $ from 'jquery'

function deck_counts() {
    if(
        $('.total_deck_count').length>0 ||
        $('.month_deck_count').length>0 ||
        $('.week_deck_count').length>0
    ) {
        $.ajax(
            "https://keyforge.tinycrease.com/deck_count?month=true&week=true", {
            success: function (data, status, xhr) {
                $('.total_deck_count').append(data.total_deck_count)
                $('.month_deck_count').append(data.month_deck_count)
                $('.week_deck_count').append(data.week_deck_count)
            },
        })
    }
}

export {deck_counts}
