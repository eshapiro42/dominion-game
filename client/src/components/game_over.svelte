<script>
    import Card from "./card.svelte";

    import sortCards from "../common.js";

    export let endGameData = {
        explanation: "",
        winners: "",
        playerData: [],
        showVictoryTokens: false,
    };

    export let show;

    let sortByProperty = "type";
    let displayAs = "row";
    let active = false;

    let sortByOptions = [
        {text: "Type", property: "type"},
        {text: "Cost", property: "cost"},
        {text: "Name", property: "name"},
        // {text: "Order Sent", property: "orderSent"},
    ]

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

    $: displayAsRow = displayAs == "row";
    $: displayAsGrid = displayAs == "grid";

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
            </div>
            <div class="endGameData">
                <br>
                <h5>{endGameData.explanation}</h5>
                <br>
                <h5>{endGameData.winners}</h5>
                <br>
                <table class="table table-hover table-bordered">
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
                                {#if playerData.victoryTokens}
                                    <td>
                                        {playerData.victoryTokens}
                                    </td>
                                {/if}
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
            <div class="dropdowns">
                <div class="sort">
                    <p>Sort By<p>
                    <select bind:value={sortByProperty}>
                        {#each sortByOptions as option}
                            <option value={option.property}>
                                {option.text}
                            </option>
                        {/each}
                    </select>
                </div>
                <div class="displayAs">
                    <p>Display As<p>
                    <select bind:value={displayAs}>
                        <option value="row">Row</option>
                        <option value="grid">Grid</option>
                    </select>
                </div>
            </div>
        
            {#each endGameData.playerData as playerData}
                <div class="title">
                    <h4>{playerData.name}'s Cards</h4>
                </div>
                <div
                    class="cards"
                    class:displayAsRow
                    class:displayAsGrid
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

    $scrollbar-color: #34333880;
    $scrollbar-color-hover: #343338;

    @keyframes blinking {
        0%, 30%, 70%, 100% {
            background-color: #fff;
        }
        50% {
            background-color: rgb(250, 226, 226);
        }
    }

    main {
        margin-top: 20px;
        border: 1px solid slategrey;

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
        animation: blinking 3s infinite;
    }

    .sort {
        margin-top: 25px;
        display: flex;
        justify-content: center;
        align-items: baseline;
        flex-wrap: nowrap;
        gap: 10px;
    }

    .displayAs {
        margin-top: 25px;
        display: flex;
        justify-content: center;
        align-items: baseline;
        flex-wrap: nowrap;
        gap: 10px;
    }

    .table {
        text-align: left;
        vertical-align: middle;
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
    }

    .dropdowns {
        display: flex;
        justify-content: center;
        gap: 100px;
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
</style>