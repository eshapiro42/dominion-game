<script>
    import {
        socket,
        room,
    } from "../stores.js";

    let showSettings = false;
    let chosenFont = null;
    let chosenTheme = null;
    let chosenCardSize = null;

    const themes = ["dark", "light"];
    const fonts = ["modern", "classic",];
    const cardSizes = ["tiny", "small", "medium", "large",];

    function capitalize(word) {
        return word && word[0].toUpperCase() + word.slice(1);
    }

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
        if (cached_theme && themes.includes(cached_theme)) {
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
        // Disable all transitions
        const css = document.createElement('style');
        css.appendChild(
            document.createTextNode(
                `* {
                    -webkit-transition: none !important;
                    -moz-transition: none !important;
                    -o-transition: none !important;
                    -ms-transition: none !important;
                    transition: none !important;
                }`
            )
        )
        document.head.appendChild(css);
        // Set the CSS attribute
        document.documentElement.setAttribute("data-theme", theme);
        // Cache the selected theme in the browser
        localStorage.setItem("theme", theme);
        // Redraw and enable transitions
        const _ = window.getComputedStyle(css).opacity;
        document.head.removeChild(css);
    }

    // On load, set to the preferred theme (if any)
    chosenTheme = getPreferredTheme();

    // On change, set to and cache the new theme
    $: setTheme(chosenTheme);

    function getPreferredFont() {
        // Check if the user has set a preference
        const cached_font = localStorage.getItem("font");
        if (cached_font && fonts.includes(cached_font)) {
            return cached_font;
        }
        else {
            return "modern";
        }
    }

    function setFont(font) {
        // Set the CSS attribute
        document.documentElement.setAttribute("font", font);
        // Cache the selected font in the browser
        localStorage.setItem("font", font);
    }

    // On load, set to the preferred font (if any)
    chosenFont = getPreferredFont();

    // On change, set and cache the font
    $: setFont(chosenFont);

    function getPreferredCardSize() {
        // Check if the user has set a preference
        const cached_card_size = localStorage.getItem("cardSize");
        if (cached_card_size && cardSizes.includes(cached_card_size)) {
            return cached_card_size;
        }
        else {
            return "medium";
        }
    }

    function setCardSize(cardSize) {
        // Set the CSS attribute
        document.documentElement.setAttribute("card-size", cardSize);
        // Cache the selected size in the browser
        localStorage.setItem("cardSize", cardSize);
    }

    // On load, set to the preferred card size (if any)
    chosenCardSize = getPreferredCardSize();

    // On change, set and cache the card size
    $: setCardSize(chosenCardSize);
</script>

<main>
    <i class="fa-solid fa-gear"
        class:showSettings
        on:click|stopPropagation={toggleSettings}
    >
    </i>

    {#if showSettings}
        <div class="settings"
            on:click|stopPropagation={()=>{}}
        >
            <select bind:value={chosenTheme}>
                {#each themes as theme}
                    <option value={theme}>
                        {capitalize(theme)} Mode
                    </option>
                {/each}

            </select>
            <select bind:value={chosenFont}>
                {#each fonts as font}
                    <option value={font}>
                        {capitalize(font)} Font
                    </option>
                {/each}
            </select>
            <select bind:value={chosenCardSize}>
                {#each cardSizes as cardSize}
                    <option value={cardSize}>
                        {capitalize(cardSize)} Cards
                    </option>
                {/each}
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
        z-index: 99999;
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

    .fa-gear {
        font-size: 30px;
    }

    .fa-gear:hover {
        cursor: pointer;
    }
</style>