<script>
    import Card from "./card.svelte";

    import sortCards from "../common.js";

    export let recommendedSets = [];
    export let recommendedSet = null;

    let sortByProperty = "cost";
    let displayAs = "row";

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

    $: recommendedSetsSorted = recommendedSets.map(
        setData => (
            {
                name: setData.name,
                expansions: setData.expansions,
                cards: sortCards(setData.cards, sortByProperty),
                additional_cards: setData.additional_cards,
            }
        )
    );
</script>

<main>
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

    {#each recommendedSetsSorted as set, index}
        <div 
            class="panel {recommendedSet == index ? "selected" : ""}"
            on:click={
                () => {
                    recommendedSet = index;
                }
            }
        >
        <hr>
            <div class="title">
                <h4>{set.name}</h4>
                <p>{set.expansions.join(", ")}<p>
            </div>
            <div
                class="cards"
                class:displayAsRow
                class:displayAsGrid
            >
                {#each set.cards as card}
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
            {#if set.additional_cards.length > 0}
                <div
                    class="cards"
                    class:displayAsRow
                    class:displayAsGrid
                >
                    {#each set.additional_cards as card}
                    <Card
                        {...card.card}
                        {waitingForSelection}
                        selectedAll=false
                        numSelected=0
                    />
                    {/each}
                </div>
            {/if}
        </div>
    {/each}
</main>


<style lang="scss">
    $margin: 5px;

    $scrollbar-color: #34333880;
    $scrollbar-color-hover: #343338;

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

    .panel {
        left: 0px;
    }

    .panel:hover:not(.selected) {
        background-color: #f0f0f0;
    }
    
    .selected {
        background-color: #cde6fe;
    }
</style>