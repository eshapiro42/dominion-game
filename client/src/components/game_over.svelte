<script>
    import Card from "./card.svelte";
    import CardDisplayOptions from "./card_display_options.svelte";

    import {sortCards} from "../common.js";

    export let endGameData = {
        explanation: "",
        winners: "",
        playerData: [],
        showVictoryTokens: false,
    };

    export let show;

    let sortByProperty;
    let displayAs;
    let active = false;

    let waitingForSelection = {
        value: false,
        handler: null,
        type: "",
        maxCards: null,
        maxCost: null,
        force: false,
        prompt: "",
        ordered: false,
    }

    $: if (show) {
        active = true;
        // Scroll to the active carousel after a short delay to allow the page to render
        setTimeout(
            () => {
                location.hash = "#Game Over";
                history.pushState("", document.title, window.location.pathname + window.location.search);
            },
            300,
        );
    }
</script>

{#if show}
    <section id="Game Over">
        <main
            class="panel"
            class:active    
        >
            <div class="title">
                <h4>Game Over</h4>
                <button
                    class="blueButton offset" style="--offset-top: -6px;"
                    on:click={
                        () => {
                            window.location.reload(true);
                        }
                    }
                >
                    Return to Lobby
                </button>
            </div>
            <div class="endGameData">
                <br>
                <h5>{endGameData.explanation}</h5>
                <br>
                <h5>{endGameData.winners}</h5>
                <br>
                <table>
                    <thead>
                        <tr>
                            <th>Player</th>
                            <th>Victory Points</th>
                            <th>Turns Taken</th>
                            {#if endGameData.showVictoryTokens}
                                <th>Victory Tokens</th>
                            {/if}
                        </tr>
                    </thead>
                    <tbody>
                        {#each endGameData.playerData as playerData}
                            <tr>
                                <td>
                                    <b>{playerData.name}</b>
                                </td>
                                <td>
                                    {playerData.score}
                                </td>
                                <td>
                                    {playerData.turns}
                                </td>
                                {#if endGameData.showVictoryTokens}
                                    <td>
                                        {#if playerData.victoryTokens}
                                            {playerData.victoryTokens}
                                        {/if}
                                    </td>
                                {/if}
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
            <CardDisplayOptions
                name="Game Over"
                bind:displayAs={displayAs}
                bind:sortByProperty={sortByProperty}
            />
        
            {#each endGameData.playerData as playerData}
                <div class="title">
                    <h4>{playerData.name}'s Cards</h4>
                </div>
                <div
                    class="cards"
                    class:displayAsRow={displayAs == "row"}
                    class:displayAsGrid={displayAs == "grid"}
                >
                    {#each sortCards(playerData.cards, sortByProperty, true) as card}
                        <Card
                            {...card}
                            {waitingForSelection}
                            selectedAll=false
                            numSelected=0
                        />
                    {:else}
                        <div class="text">
                            <p>Nothing here!</p>
                        </div>
                    {/each}
                </div>
            {/each}
        </main>
    </section>
{/if}

<style lang="scss">
    $margin: 5px;

    $scrollbar-color: color-mix(in srgb, var(--blue-color), var(--body-background-color) 20%);
    $scrollbar-color-hover: var(--blue-color);

    main {
        margin-top: 20px;
        border: 1px solid var(--border-color);

        ::-webkit-scrollbar {
            height: 10px;
        }
        ::-webkit-scrollbar-track {
            background-color: transparent;
        }
        ::-webkit-scrollbar-thumb {
            border-radius: 20px;
            border: 2px solid transparent;
            background-clip: content-box;
            background-color: $scrollbar-color;
        }
        ::-webkit-scrollbar-thumb:hover {
            background-color: $scrollbar-color-hover;
        }
    }

    .active {
        animation: blinking 3s infinite ease-in-out;
    }

    .text {
        display: flex;
        width: 100%;
        height: 100%;
        position: relative;
        text-align: center;
        justify-content: center;
    }

    .title {
        width: 100%;
        height: 100%;
        text-align: center;
        margin-top: 25px;
        display: flex;
        flex-direction: row;
        justify-content: center;
        gap: 30px;
    }

    .cards {
        flex-basis: 100%;
        display: flex;
        overflow-x: auto;
        flex-wrap: nowrap;
        padding-left: 10px;
        padding-right: 10px;
        padding-bottom: 10px;
        padding-top: 25px;
        text-align: center;
    }

    .displayAsRow {
        flex-wrap: nowrap;
    }

    .displayAsGrid {
        flex-wrap: wrap;
        row-gap: 5px;
    }

    table {
        min-width: 0px;
        left: 0px;
        border-left: none;
        border-right: none;
        color: var(--text-color);
    }
</style>