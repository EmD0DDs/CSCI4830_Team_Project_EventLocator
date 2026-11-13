const params = new URLSearchParams(window.location.search);
// Browsers only allow geolocation on HTTPS (or localhost); otherwise the server falls back to Omaha
if (window.isSecureContext && navigator.geolocation && (!params.has('lat') || !params.has('lon'))) {
    navigator.geolocation.getCurrentPosition( 
    (position) => {
        
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        window.location.href = `/home/?lat=${lat}&lon=${lon}`;
    },
    (error) => {
        console.warn("EventLocator: location unavailable, showing events near Omaha.");
    }
    ); 
}


