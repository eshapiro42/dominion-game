<script>
    import {createEventDispatcher} from "svelte";

    const dispatch = createEventDispatcher();

    import Card from "./card.svelte";
    import CardDisplayOptions from "./card_display_options.svelte";
    import SelectionPrompt from "./selection_prompt.svelte";

    import {activeCarousel, username, currentPlayer} from "../stores.js";

    import {flashTitle, sortCards} from "../common.js";

    export let title;
    export let waitingForSelection;
    export let invalidCardNames = [];
    export let invalidCardIds = [];
    export let sortByProperty;

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
    let displayAs;
    let cardRefs = [];

    $: sortedCards = sortCards(cards, sortByProperty);

    $: numSelected = selectedCardIds.length;

    $: active = waitingForSelection.value;

    $: if (active) {
        activeCarousel.set(title);
        // Scroll all cards in the carousel back to the top
        cardRefs.forEach(
            (cardRef) => {
                if (cardRef) {
                    cardRef.scrollToTop();
                }
            }
        );
        setTimeout(
            () => {
                // Scroll to the active carousel after a short delay to allow the page to render
                location.hash = "#" + title;
                history.pushState("", document.title, window.location.pathname + window.location.search);
   
                // If it is another player's turn, flash the tab title
                if ($username != $currentPlayer) {
                    flashTitle("You Must React!");
                    alert(`Heads up: It is still ${$currentPlayer}'s turn!`);
                }
            },
            300,
        );
    }
    else {
        activeCarousel.set(null);
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
        // Find the selected cards by ID while maintaining order of selection
        var selectedCards = selectedCardIds.map(
            (id) => {
                return cards.find(
                    (card) => {
                        return card.id == id;
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

<section id="{title}">
    <main
        class="panel"
        class:active
    >
        <CardDisplayOptions
            name={title}
            illegalSortByOptions={title == "Supply" ? ["orderSent"] : []}
            bind:displayAs={displayAs}
            bind:sortByProperty={sortByProperty}
        />
        <div class="title">
            {#if (title == "Prizes")}
                <div class="hoverable">
                    <h4>{title}</h4>
                    <span class="hoverable-text">
                        <span>
                            Prizes are unique cards that are not in the Supply and can only be gained by playing a Tournament.
                        </span>
                        <span>
                            If the Prizes run out, it does not count toward the game end condition.
                        </span>
                        <span>
                            Trashed Prizes go into the Trash pile, like any other card.
                        </span>
                    </span>
                </div>
            {:else}
                <h4>{title}</h4>
            {/if}
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
            class:displayAsRow={displayAs == "row"}
            class:displayAsGrid={displayAs == "grid"}
        >
            {#each sortedCards as card, index (card.id)}
                <Card
                    bind:this={cardRefs[index]}
                    {...card}
                    {invalidCardNames}
                    {invalidCardIds}
                    {waitingForSelection}
                    {selectedAll}
                    {numSelected}
                    {selectedCardIds}
                    on:clicked={handleClicked}
                />
            {:else}
                <div class="text">
                    <p>Nothing here!</p>
                </div>
            {/each}
        </div>
    </main>
</section>

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
        animation: blinking var(--blinking-speed) infinite linear;
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