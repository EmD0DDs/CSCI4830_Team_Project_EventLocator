# Home and Host Event — frontend

**Kenneth — frontend contribution**

I built the Home and Host Event page designs within our existing Django `HomePage` app. The team's login/signup, API, and database code remain unchanged.

**Home:** Omaha banner, 3-second shuffled slideshow, categories, sample event cards, and scroll animations. The event cards are placeholders, and bookmarks are not saved.

**Host Event:** Event creation form with the approved Omaha background. Submitting currently shows a preview message; it does not create a database record.

**For integration:** Use our API/database to populate the event cards in `templates/home.html`, connect bookmarks to users, and connect `#event-form` in `templates/host_event.html` to a Django POST view (including CSRF protection). The Host Event URL is `/home/host-event/`.

The 20 slideshow photos are still stored locally on my computer. Add them to `static/HomePage/images/slides/` and list their filenames in `static/HomePage/js/slideshow-manifest.js`.
