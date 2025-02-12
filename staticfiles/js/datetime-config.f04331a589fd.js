document.addEventListener('DOMContentLoaded', function() {
    // Configure datetime inputs
    const datetimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    datetimeInputs.forEach(input => {
        // Set first day of week to Monday
        input.addEventListener('click', function(e) {
            const calendar = document.querySelector('.calendar');
            if (calendar) {
                calendar.firstDay = 1;
            }
        });

        // Format the displayed date
        input.addEventListener('change', function(e) {
            const date = new Date(this.value);
            if (!isNaN(date)) {
                const options = { 
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    weekday: 'long'
                };
                const formattedDate = date.toLocaleDateString('lt-LT', options);
                this.title = formattedDate;
            }
        });
    });
}); 