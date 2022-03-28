<script>
    import Card from "./card.svelte";

    export let title;

    export let cards = [ // Default cards are only present for easy prototyping
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

    export function addCard(card_data) {
        cards = cards.concat(card_data)
    }

    let cardTitle = "";
    let cardDescription = "";
    let cardCost = "";
    let cardType = "";
    // let highestId = 0;
    let sortByProperty = "name";

    let sortByOptions = [
        {text: "Name", property: "name"},
        {text: "Type", property: "type"},
        {text: "Cost", property: "cost"},
    ]

    $: sortedCards = cards.sort((a, b) => {
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
</script>

<main>
    <div class="title">
        <h4>{title}</h4>
    </div>

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

    <div class="container">
        {#each sortedCards as card (card.id)}
            <Card {...card}/>
        {:else}
            <div class="text">
                <p>Nothing here!</p>
            </div>
        {/each}
    </div>

    <!-- <div class="helper">
        <input placeholder="Title" bind:value={cardTitle}/>
        <input placeholder="Description" bind:value={cardDescription}/>
        <input placeholder="Cost" bind:value={cardCost}/>
        <input placeholder="Type" bind:value={cardType}/>
        <button on:click= {
            () => {
                addCard({
                    name: cardTitle,
                    effects: "",
                    description: cardDescription,
                    cost: cardCost,
                    type: cardType,
                    id: highestId,
                });
                highestId += 1;
            }
        }>Add Card</button>
    </div> -->
</main>

<style lang="scss">
    $margin: 5px;

    main {
        margin-top: 20px;
    }

    .sort {
        margin-top: 20px;
        display: flex;
        justify-content: center;
        align-items: baseline;
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
    }

    .container {
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

    .helper {
        margin-top: 20px;
    }
</style>