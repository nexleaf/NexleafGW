$(document).ready(function() {
    
    // Make data table rows highlight on hover.
    if ($('.data_table').length !== 0) {
        $(".data_table td").hover(
            function() {
                $(this).parents('.data_table tr').addClass('highlight');
            }, function() {
                $(this).parents('.data_table tr').removeClass('highlight');
            }
        );
    }
});
