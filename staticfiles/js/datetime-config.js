// Datos ir laiko formatavimo konfigūracija pagal vartotojo kalbą
document.addEventListener('DOMContentLoaded', function() {
    // Gauti dabartinę kalbą iš HTML elemento
    const currentLanguage = document.documentElement.lang || 'lt';
    
    // Datos formatavimo nustatymai pagal kalbą
    const dateFormatOptions = {
        lt: {
            date: { year: 'numeric', month: 'long', day: 'numeric' },
            time: { hour: '2-digit', minute: '2-digit' },
            dateTime: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
            shortDate: { year: 'numeric', month: '2-digit', day: '2-digit' }
        },
        en: {
            date: { year: 'numeric', month: 'long', day: 'numeric' },
            time: { hour: '2-digit', minute: '2-digit' },
            dateTime: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
            shortDate: { year: 'numeric', month: '2-digit', day: '2-digit' }
        }
    };
    
    // Numatytieji nustatymai, jei kalba nėra palaikoma
    const defaultFormat = dateFormatOptions.lt;
    
    // Gauti formatavimo nustatymus pagal kalbą
    const formatOptions = dateFormatOptions[currentLanguage] || defaultFormat;
    
    // Formatuoti visus datos elementus
    const dateElements = document.querySelectorAll('[data-datetime]');
    dateElements.forEach(element => {
        const dateType = element.dataset.datetime; // date, time, datetime
        const dateValue = element.dataset.value;
        
        if (dateValue) {
            const date = new Date(dateValue);
            
            if (!isNaN(date.getTime())) {
                let formattedValue = '';
                
                switch (dateType) {
                    case 'date':
                        formattedValue = date.toLocaleDateString(currentLanguage, formatOptions.date);
                        break;
                    case 'time':
                        formattedValue = date.toLocaleTimeString(currentLanguage, formatOptions.time);
                        break;
                    case 'datetime':
                        formattedValue = date.toLocaleString(currentLanguage, formatOptions.dateTime);
                        break;
                    case 'shortdate':
                        formattedValue = date.toLocaleDateString(currentLanguage, formatOptions.shortDate);
                        break;
                    default:
                        formattedValue = date.toLocaleString(currentLanguage);
                }
                
                element.textContent = formattedValue;
            }
        }
    });
    
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
                const formattedDate = date.toLocaleDateString(currentLanguage, options);
                this.title = formattedDate;
            }
        });
    });
}); 