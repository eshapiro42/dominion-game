<script>
    import {
            socket,
            classicFont,
            dataTheme,
            room,
        } from "../stores.js";

    let showSettings = false;

    function toggleSettings() {
        showSettings = !showSettings;
        if (showSettings) {
            document.body.addEventListener('click', toggleSettings);
        }
        else{
            document.body.removeEventListener('click', toggleSettings);
        }
    }

    $: if ($dataTheme !== null) {
        document.documentElement.setAttribute("data-theme", $dataTheme);
    }
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
            <select bind:value={$dataTheme}>
                <option value="dark">
                    Dark Mode
                </option>
                <option value="light">
                    Light Mode
                </option>
            </select>
            <select bind:value={$classicFont}>
                <option value={false}>
                    Modern Font
                </option>
                <option value={true}>
                    Classic Font
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