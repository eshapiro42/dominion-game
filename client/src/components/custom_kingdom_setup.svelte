<script>
    import Card from "./card.svelte";
    import CardDisplayOptions from "./card_display_options.svelte";

    import {sortCards} from "../common.js";

    export let customKingdomData = {};
    export let allKingdomCards = [];
    export let cards = [];

    let allKingdomCardsSorted = [];
    let baneCard = null;
    let usePlatinumAndColony = null;
    let invalidCardIds = [];
    let sortByProperty = "cost";
    let displayAs;
    let selectedAll = false;
    let selectedCardIds = [];
    let selectedCardNames = [];
    let youngWitchSelected = false;
    let availableBaneCards = [];
    let waitingForSelection = {
        value: true,
        handler: null,
        type: "",
        maxCards: 10,
        maxCost: null,
        force: false,
        prompt: "",
        ordered: true,
    }

    $: numSelected = selectedCardIds.length;

    $: availableBaneCards = allKingdomCards
        .flatMap(expansion => expansion.cards)
        .filter(card => card.cost <=3)
        .filter(card => !selectedCardNames.includes(card.name));

    $: allKingdomCardsSorted = allKingdomCards.map(
        expansionData => (
            {
                expansion: expansionData.expansion,
                cards: sortCards(expansionData.cards, sortByProperty),
            }
        )
    );

    $: if (baneCard !== null) {
        invalidCardIds = [baneCard.id]
    } else {
        invalidCardIds = [];
    }    

    $: customKingdomData = {
        cards: selectedCardNames,
        bane_card_name: baneCard !== null ? baneCard.name : null,
        use_platinum_and_colony: usePlatinumAndColony
    }

    function handleClicked(event) {
        selectedAll = false;
        var cardSelected = event.detail.selected;
        var cardId = event.detail.id;
        var cardName = event.detail.name;
        if (cardSelected) {
            if (!cards.some(card => card.id === cardId)) {
                cards = cards.concat(event.detail)
            }
            selectedCardIds = selectedCardIds.concat(cardId);
            selectedCardNames = selectedCardNames.concat(cardName);
            if (cardName === "Young Witch") {
                youngWitchSelected = true;
            }
        }
        else {
            selectedCardIds = selectedCardIds.filter(
                (selectedCardId) => {
                    return selectedCardId != cardId;
                }
            );
            selectedCardNames = selectedCardNames.filter(
                (selectedCardName) => {
                    return selectedCardName != cardName;
                }
            );
            if (cardName === "Young Witch") {
                youngWitchSelected = false;
                baneCard = null;
            }
        }
    }
</script>

<main>
    <CardDisplayOptions
        name="Custom Kingdom Setup"
        illegalSortByOptions={["orderSent"]}
        bind:displayAs={displayAs}
        bind:sortByProperty={sortByProperty}
    />
    {#each allKingdomCardsSorted as expansionData}
        <div class="expansion">
            <div class="title">
                <h4>{expansionData.expansion}</h4>
            </div>
            {#if youngWitchSelected && expansionData.expansion == "Cornucopia"}
                Bane Card
                <select bind:value={baneCard}>
                    <option value={null} selected>Random</option>
                    {#each availableBaneCards as availableBaneCard}
                        <option value={availableBaneCard}>{availableBaneCard.name}</option>
                    {/each}
                </select>
            {:else if expansionData.expansion == "Prosperity"}
                Use Platinum and Colony?
                <select bind:value={usePlatinumAndColony}>
                    <option value={null} selected>Random</option>
                    <option value={true}>Yes</option>
                    <option value={false}>No</option>
                </select>
            {/if}
            <div
                class="cards"
                class:displayAsRow={displayAs == "row"}
                class:displayAsGrid={displayAs == "grid"}
            >
                {#each expansionData.cards as card (card.id)}
                    <Card
                        {...card}
                        forceBane={card == baneCard}
                        {waitingForSelection}
                        {selectedAll}
                        {numSelected}
                        {selectedCardIds}
                        {invalidCardIds}
                        on:clicked={handleClicked}
                    />
                {:else}
                    <div class="text">
                        <p>Nothing here!</p>
                    </div>
                {/each}
            </div>
        </div>
    {/each}
</main>


<style lang="scss">
    $margin: 5px;

    $scrollbar-color: color-mix(in srgb, var(--blue-color), var(--body-background-color) 20%);
    $scrollbar-color-hover: var(--blue-color);

    main {
        border: 1px solid var(--border-color);
        border-top: none;

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
        margin-bottom: 25px;
    }

    .cards {
        flex-basis: 100%;
        display: flex;
        overflow-x: auto;
        flex-wrap: nowrap;
        padding-left: 10px;
        padding-right: 10px;
        padding-bottom: 10px;
        padding-top: 30px;
        text-align: center;
    }

    .displayAsRow {
        flex-wrap: nowrap;
    }

    .displayAsGrid {
        flex-wrap: wrap;
        row-gap: 5px;
    }

    .expansion {
        left: 0px;
        padding-top: 30px;
        border-bottom: var(--hrule);
    }
</style>