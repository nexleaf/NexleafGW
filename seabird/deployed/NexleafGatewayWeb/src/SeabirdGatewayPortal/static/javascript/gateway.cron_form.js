$(document).ready(function() {
    
    // Select All / Deselect all hours for cron form.
    $('.select_all_hours').click(function() {
        $('input[name="cron_hours"]').attr('checked','checked');
    });
    
    $('.select_none').click(function() {
        $('input[name="cron_hours"]').removeAttr('checked');
    });
    
});