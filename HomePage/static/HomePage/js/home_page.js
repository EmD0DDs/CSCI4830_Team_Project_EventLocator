navigator.geolocation.getCurrentPosition( 
    (position) => {
        
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        window.location.href = `/home/?lat=${lat}&lon=${lon}`;
    },
    (error) => {
        alert("We couldn't get your location. Please type your city instead.");
    }
); 
