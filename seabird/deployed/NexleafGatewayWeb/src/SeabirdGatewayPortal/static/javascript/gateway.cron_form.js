$(document).ready(function() {
    
    // Select All / Deselect all hours for cron form.
    $('.select_all_hours_killfm').click(function() {
        $('input[name="cron_hours_killfm"]').attr('checked','checked');
    });
    
    $('.select_none_killfm').click(function() {
        $('input[name="cron_hours_killfm"]').removeAttr('checked');
    });

    $('.select_all_hours_audio').click(function() {
        $('input[name="cron_hours_audio"]').attr('checked','checked');
    });
    
    $('.select_none_audio').click(function() {
        $('input[name="cron_hours_audio"]').removeAttr('checked');
    });

    $('.select_all_hours_logs').click(function() {
        $('input[name="cron_hours_logs"]').attr('checked','checked');
    });
    
    $('.select_none_logs').click(function() {
        $('input[name="cron_hours_logs"]').removeAttr('checked');
    });
    
});