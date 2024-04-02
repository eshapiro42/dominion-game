<script>
    import {afterUpdate, beforeUpdate, onMount, tick} from "svelte";
    import {socket, currentPlayer} from "../stores.js";

    let show = true;

    let entries = [];
    let scrollContainer = null;
    let scrolledToBottom = true;

    $: if (show) {
        document.documentElement.style.setProperty("--gamelog-width", "256px");
    } 
    else {
        document.documentElement.style.setProperty("--gamelog-width", "0px");
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
        // Check if entry should be italicized (kind of a hack but YOLO)
        if (entry.message.includes("→")) {
            entry.italicize = true;
        }
        // Append the new log entry
        entries = [...entries, entry];
    }

    beforeUpdate(
        () => {
            if (scrollContainer) {
                // Detect whether the log is already scrolled all the way down
                scrolledToBottom = scrollContainer.scrollHeight - Math.ceil(scrollContainer.scrollTop) <= scrollContainer.clientHeight + 64;
            }
        }
    );

    afterUpdate(
        () => {
            if (scrollContainer && scrolledToBottom) {
                // If the log was scrolled all the way down, scroll to the bottom again
                scrollContainer.scrollTop = scrollContainer.scrollHeight;
            }
        }
    );

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
            <div class="entry {entry.hasOwnProperty("new_turn") ? "newTurn" : ""} {entry.hasOwnProperty("new_phase") ? "newPhase": ""} {entry.hasOwnProperty("disconnect") ? "disconnect": ""} {entry.hasOwnProperty("italicize") ? "italicize": ""}">
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
        font-size: 85%;
        text-align: start;

        ::-webkit-scrollbar {
            width: 10px;
        }
        ::-webkit-scrollbar-track {
            background-color: var(--body-background-color);
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
        margin-right: -10px;
        padding-right: 10px;
    }

    .entry.italicize > .message{
        font-style: italic;
    }

    .entry:hover {
        background-color: color-mix(in srgb, var(--victory-card-color) 20%, var(--thead-background-color) 80%);
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
        background-color: color-mix(in srgb, var(--blue-color) 20%, var(--thead-background-color) 80%);
        margin-left: -10px;
        padding-left: 10px;
        font-weight: bold;
    }

    .newPhase {
        padding-left: 10px;
        font-weight: bold;
    }

    .disconnect {
        background-color: color-mix(in srgb, var(--attack-card-color) 10%, var(--thead-background-color) 90%);
        margin-left: -10px;
        padding-left: 10px;
    }

    /* Do not show game log on mobile devices */
    @media (max-width: 767px) {
        main {
             display: none;
        }
    }
</style>
