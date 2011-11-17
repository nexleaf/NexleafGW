$(document).ready(function() {
    
    // Add recording form dynamically
    $('.add_recording').live('click', function(e) {
        e.preventDefault();
        add_formset('div.recording_container:last', 'recordingform');
        
        // Update recording counts displayed to the user.
        recording_count_updater();
    });
    
    // Remove recording form dynamically
    $('.remove_recording').live('click', function(e) {
        e.preventDefault();
                
        // Grab parent container
        var container = $(this).closest('div.recording_container');
        remove_formset(container);
        
        // Update recording counts displayed to the user.
        recording_count_updater();
    });
    
    // Display Only - updates the numbers on the various recording schedules
    // Run after each time a recording is added or removed.
    function recording_count_updater() {
        var recording_counter = 1;
        $('div.recording_container:not(:hidden)').each(function() {
            $(this).find('span.recording_number').text(recording_counter)
            recording_counter++;
        });
    }
    
    // Genericized way to add a new formset.
    function add_formset(selector, prefix) {
        elements = clone_formset(selector, prefix)
        
        // Unhide remove links (if hidden).
        if (elements.newElement.find('.remove_recording_container').hasClass('hide')) {
            elements.newElement.find('.remove_recording_container').removeClass('hide');
        }

        // Make sure new element not "hidden" if it was cloned from a previously "removed" element.
        elements.newElement.show();
        
        // TODO: Make sure new element not "deleted" if it was cloned from a deleted element.
        
        return elements;
    }
    
    // Function for removing formsets (delete and hide).
    function remove_formset(container) {
        // clear the value of all fields
        container.find(':input:not(:hidden)').each(function() {
           $(this).val('');
        });
        
        // set delete to "on" for corresponding db records to be deleted on submit
        container.find('input[id$=-DELETE]').val('on');
        
        // Hide form - will still be used for cloning purposes.
        container.hide();
        
        // TOTAL doesn't get updated because the form still exists (it's just hidden and "deleted".)
    }
    
    // Clones a formset element.
    // Inspired By: http://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset-with-ajax
    function clone_formset(selector, prefix) {
        var originalElement = $(selector);
        var newElement = $(selector).clone(true);
        var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
        newElement.find(':input').each(function() {
            var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
            console.log(id);
        });
        newElement.find('label').each(function() {
            var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
            $(this).attr('for', newFor);
        });
        total++;
        $('#id_' + prefix + '-TOTAL_FORMS').val(total);
        $(selector).after(newElement);
        
        return {originalElement:originalElement, newElement:newElement};
    }
    
    // Update recording counts on document ready.
    recording_count_updater()
});