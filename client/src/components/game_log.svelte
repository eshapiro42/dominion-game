<script>
    import {onMount, tick} from "svelte";
    import {socket, currentPlayer} from "../stores.js";

    let show = true;

    let entries = [];
    let scrollContainer = null;

    $: if (show) {
        document.documentElement.style.setProperty("--gamelog-width", "256px");
    } 
    else {
        document.documentElement.style.setProperty("--gamelog-width", "0");
    }

    onMount(
        () => {
            newEntry({
                "new_turn": true,
                "timestamp": new Date().toLocaleTimeString(),
                "message": "Welcome to Dominion!",
            });
        }
    );

    function newEntry(entry) {
        // Detect whether the log is already scrolled all the way down
        var scrolledToBottom = scrollContainer.scrollHeight - Math.ceil(scrollContainer.scrollTop) <= scrollContainer.clientHeight;
        // Append the new log entry
        entries = [...entries, entry];
        // If the log was scrolled all the way down, scroll to the bottom again
        if (scrolledToBottom) {
            tick().then(() => {
                scrollContainer.scrollTop = scrollContainer.scrollHeight;
            });
        }
    }

    $socket.on(
        "message",
        (entry) => {
            if (!entry.hasOwnProperty("timestamp")) {
                entry = {
                    "timestamp": new Date().toLocaleTimeString(),
                    "message": entry,
                }
            }
            else {
                entry.timestamp = new Date(entry.timestamp).toLocaleTimeString();
            }
            newEntry(entry);
        }
    );

    $socket.on(
        "disconnect", 
        (reason) => {
            const entry = {
                "disconnect": true,
                "timestamp": new Date().toLocaleTimeString(),
                "message": `You have become disconnected from the server. Reason: ${reason}.`,
            }
            newEntry(entry);
        }
    );

    $socket.on(
        "new phase",
        (phase_name) => {
            const entry = {
                "new_phase": true,
                "timestamp": new Date().toLocaleTimeString(),
                "message": phase_name,
            }
            newEntry(entry);
        }
    )

    $: if ($currentPlayer != "") {
        const entry = {
            "new_turn": true,
            "timestamp": new Date().toLocaleTimeString(),
            "message": `${$currentPlayer}'s Turn!`,
        }
        newEntry(entry);
    }

    // $socket.on("player message", function(data) {
    //     addMessage(data, true);
    // });
</script>

<main>
    <div class="scroll-container" bind:this={scrollContainer}>
        {#each entries as entry}
            <div class="entry {entry.hasOwnProperty("new_turn") ? "newTurn" : ""} {entry.hasOwnProperty("new_phase") ? "newPhase": ""} {entry.hasOwnProperty("disconnect") ? "disconnect": ""}">
                <div class="timestamp">
                    {entry.timestamp}
                </div>
                <div class="message">
                    {entry.message}
                </div>
            </div>
        {/each}
    </div>
</main>

<style lang="scss">
    $light-scrollbar-color: #d9d9d980;
    $light-scrollbar-color-hover: #dadada;

    main {
        z-index: 9999;
        right: 0;
        top: 0;
        width: 256px;
        height: 100%;
        position: fixed;
        background-color: var(--thead-background-color);
        color: var(--light-text-color);
        border-left: 1px solid var(--border-color);
        font-family: var(--title-font-family);
        font-size: 80%;
        text-align: start;

        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background-color: transparent;
        }
        ::-webkit-scrollbar-thumb {
            border-radius: var(--card-border-radius);
            border: 2px solid transparent;
            background-clip: content-box;
            background-color: $light-scrollbar-color;
        }
        ::-webkit-scrollbar-thumb:hover {
            background-color: $light-scrollbar-color-hover;
        }
    }

    .scroll-container {
        max-height: 100%;
        overflow-y: auto;
        overflow-x: hidden;
        direction: rtl;
        padding-left: 10px;
        padding-right: 10px;
    }

    .entry {
        direction: ltr;
        padding-top: 5px;
        padding-bottom: 5px;
    }

    .entry:not(.newTurn):not(.newPhase):not(.disconnect) {
        padding-left: 10px;
        margin-left: 10px;
        border-left: 1px solid color-mix(in srgb, var(--blue-color) 20%, var(--thead-background-color) 80%);
    }

    .timestamp {
        font-weight: bold;
        color: color-mix(in srgb, var(--light-text-color) 60%, var(--thead-background-color) 40%);
        font-size: 80%;
    }

    .newTurn {
        background-color: color-mix(in srgb, var(--blue-color) 10%, var(--thead-background-color) 90%);
        margin-left: -10px;
        margin-right: -10px;
        padding-left: 10px;
        padding-right: 10px;
    }

    .newPhase {
        background-color: color-mix(in srgb, var(--attack-card-color) 5%, var(--thead-background-color) 95%);
        margin-right: -10px;
        padding-left: 10px;
        padding-right: 10px;
    }

    .disconnect {
        background-color: var(--attack-card-color);
        color: var(--dark-text-color);
        margin-left: -10px;
        margin-right: -10px;
        padding-left: 10px;
        padding-right: 10px;
    }

    /* Do not show game log on mobile devices */
    @media (max-width: 767px) {
        main {
             display: none;
        }
    }
</style>
