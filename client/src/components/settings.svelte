<script>
    import {
        socket,
        chosenFont,
        room,
    } from "../stores.js";

    let showSettings = false;
    let chosenTheme = null;
    let chosenCardSize = null;

    function toggleSettings() {
        showSettings = !showSettings;
        if (showSettings) {
            document.body.addEventListener('click', toggleSettings);
        }
        else{
            document.body.removeEventListener('click', toggleSettings);
        }
    }

    // Getters and setters

    function getPreferredTheme() {
        // Check if the user has set a preference
        const cached_theme = localStorage.getItem("theme");
        if (cached_theme) {
            return cached_theme;
        }
        // Check if the user has a preferred color scheme
        const query = window.matchMedia(
            "(prefers-color-scheme: dark)"
        );
        if (query.matches) {
            return "dark";
        }
        return "light";
    }

    function setTheme(theme) {
        // Set the theme variable
        chosenTheme = theme;
        // Update the page
        document.documentElement.setAttribute("data-theme", theme);
        // Cache the selected theme in the browser
        localStorage.setItem("theme", theme);
    }

    // On load, set to the preferred theme (if any)
    setTheme(getPreferredTheme());

    // On change, set to and cache the new theme
    $: setTheme(chosenTheme);

    function getPreferredFont() {
        // Check if the user has set a preference
        const cached_font = localStorage.getItem("font");
        if (cached_font) {
            return cached_font;
        }
        else {
            return "modern";
        }
    }

    function setFont(font) {
        // Set the font store variable
        $chosenFont = font;
        // Cache the selected font in the browser
        localStorage.setItem("font", font);
    }

    // On load, set to the preferred font (if any)
    setFont(getPreferredFont());

    // On change, set and cache the font
    $: setFont($chosenFont);

    function getPreferredCardSize() {
        // Check if the user has set a preference
        const cached_card_size = localStorage.getItem("cardSize");
        if (cached_card_size) {
            return cached_card_size;
        }
        else {
            return "200px";
        }
    }

    function setCardSize(cardSize) {
        // Set the card size variable
        chosenCardSize = cardSize;
        // Set the CSS variable
        document.querySelector(":root").style.setProperty("--card-width", cardSize);
        // Cache the selected size in the browser
        localStorage.setItem("cardSize", cardSize);
    }

    // On load, set to the preferred card size (if any)
    setCardSize(getPreferredCardSize());

    // On change, set and cache the card size
    $: setCardSize(chosenCardSize);
</script>

<main>
    <i class="fa-solid fa-sliders"
        class:showSettings
        on:click|stopPropagation={toggleSettings}
    >
    </i>

    {#if showSettings}
        <div class="settings"
            on:click|stopPropagation={()=>{}}
        >
            <select bind:value={chosenTheme}>
                <option value="dark">
                    Dark Mode
                </option>
                <option value="light">
                    Light Mode
                </option>
            </select>
            <select bind:value={$chosenFont}>
                <option value="modern">
                    Modern Font
                </option>
                <option value="classic">
                    Classic Font
                </option>
            </select>
            <select bind:value={chosenCardSize}>
                <option value="160px">
                    Small Cards
                </option>
                <option value="200px">
                    Normal Cards
                </option>
            </select>
            <button 
                class="blueButton"
                on:click|stopPropagation={
                    () => {
                        $socket.emit(
                            "request kingdom json",
                            {room: $room}
                        );
                    }
                }
            >
                Save Kingdom
            </button>
            <button
            class="blueButton"
                on:click={
                    () => {
                        $socket.emit(
                            "refresh",
                            {
                                room: $room,
                            }
                        );
                    }
                }
            >
                Force Refresh
            </button>
        </div>
    {/if}
</main>

<style>
    main {
        z-index: 1000000000;
    }

    .settings {
        position: absolute;
        gap: 5px;
        padding: 10px;
        height: auto;
        margin: 5px;
        max-height: 50vh;
        background-color: var(--thead-background-color);
        border: 1px solid var(--border-color);
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }

    .showSettings{
        color: var(--blue-color);
    }

    .fa-sliders {
        font-size: 30px;
    }
</style>