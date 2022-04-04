<script>
    import {createEventDispatcher} from "svelte";

    const dispatch = createEventDispatcher();

    import Card from "./card.svelte";
    import SelectionPrompt from "./selection_prompt.svelte";

    export let title;
    export let waitingForSelection;
    export let sortByProperty = "type";
    export let invalidCards = [];

    export let cards = [ 
        // This is the "source of truth" for all cards in the front-end
        // Default cards are only present for easy prototyping
        {
            name: "Copper",
            effects: "",
            description: "",
            cost: 0,
            type: "Treasure",
            id: -1,
        },
        {
            name: "Silver",
            effects: "",
            description: "",
            cost: 3,
            type: "Treasure",
            id: -2,
        },
        {
            name: "Gold",
            effects: "",
            description: "",
            cost: 6,
            type: "Treasure",
            id: -3,
        },
        {
            name: "Estate",
            effects: "",
            description: "",
            cost: 2,
            type: "Victory",
            id: -4,
        },
        {
            name: "Duchy",
            effects: "",
            description: "",
            cost: 5,
            type: "Victory",
            id: -5,
        },
        {
            name: "Province",
            effects: "",
            description: "",
            cost: 8,
            type: "Victory",
            id: -6,
        },
        {
            name: "Curse",
            effects: "",
            description: "",
            cost: 0,
            type: "Curse",
            id: -7,
        },
    ]

    let selectedAll = false;
    let selectedCardIds = [];

    let displayAs = "row";

    $: displayAsRow = displayAs == "row";
    $: displayAsGrid = displayAs == "grid";

    let sortByOptions = [
        {text: "Type", property: "type"},
        {text: "Cost", property: "cost"},
        {text: "Name", property: "name"},
        {text: "Order Sent", property: "orderSent"},
    ]

    $: sortedCards = cards.sort(
        (a, b) => {
            if (sortByProperty == "orderSent") {
                return 0;
            }
            if (a[sortByProperty] < b[sortByProperty]) {
                return -1;
            }
            else if (a[sortByProperty] > b[sortByProperty]) {
                return 1;
            }
            else {
                return 0;
            }
        }
    );

    $: numSelected = selectedCardIds.length;

    $: active = waitingForSelection.value;

    $: if (active) {
        // Scroll to the active carousel after a short delay to allow the page to render
        setTimeout(
            () => {
                location.hash = "#" + title;
            },
            300,
        );
    }

    function handleClicked(event) {
        selectedAll = false;
        var cardSelected = event.detail.selected;
        var cardId = event.detail.id;
        if (cardSelected) {
            selectedCardIds = selectedCardIds.concat(cardId);
        }
        else {
            selectedCardIds = selectedCardIds.filter(
                (selectedCardId) => {
                    return selectedCardId != cardId;
                }
            );
        }
    }

    function sendSelection() {
        var selectedCards = cards.filter(
            (card) => {
                return selectedCardIds.some(
                    (selectedCardId) => {
                        return card.id == selectedCardId;
                    }
                );
            }
        );
        dispatch(
            "selected",
            {
                selectedCards: selectedCards,
            }
        );
        selectedCardIds = [];
    }
</script>

<a id="{title}">
    <main
        class="container"
        class:active    
    >
        <div class="title">
            <h4>{title}</h4>
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
        </div>

        {#if waitingForSelection.value}
            <div class="selectionPrompt">
                <SelectionPrompt 
                    {waitingForSelection}
                    on:sendSelection={sendSelection}
                    on:selectAll={
                        () => {
                            selectedAll = true;
                        }
                    }
                />
            </div>
        {/if}

        <div
            class="cards"
            class:displayAsRow
            class:displayAsGrid
        >
            {#each sortedCards as card (card.id)}
                <Card
                    {...card}
                    {invalidCards}
                    {waitingForSelection}
                    {selectedAll}
                    {numSelected}
                    on:clicked={handleClicked}
                />
            {:else}
                <div class="text">
                    <p>Nothing here!</p>
                </div>
            {/each}
        </div>
    </main>
</a>

<style lang="scss">
    $margin: 5px;

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

    .selectionPrompt {
        flex-basis: 100%;
        display: flex;
        overflow-x: auto;
        flex-wrap: nowrap;
        padding: 10px;
        text-align: center;
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