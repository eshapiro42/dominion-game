<script>
    import Card from "./card.svelte";
    import CardDisplayOptions from "./card_display_options.svelte";

    import {sortCards} from "../common.js";

    export let recommendedSets = [];
    export let recommendedSet = null;

    let sortByProperty = "cost";
    let displayAs;
    let showCardDisplayOptions = false;

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

    function toggleCardDisplayOptions() {
        showCardDisplayOptions = !showCardDisplayOptions;
        if (showCardDisplayOptions) {
            document.body.addEventListener('click', toggleCardDisplayOptions);
        }
        else{
            document.body.removeEventListener('click', toggleCardDisplayOptions);
        }
    }
</script>

<main>
    <i class="fa-solid fa-gear"
        class:showCardDisplayOptions
        on:click|stopPropagation={toggleCardDisplayOptions}
    >
    </i>
    <div class="selectedKingdom">
        <h5 class=selectionText>
            {#if recommendedSet != null}
                    Selected Kingdom: 
                    <div class="fakeLink"
                        on:click={
                            () => {
                                document.getElementById(recommendedSets[recommendedSet].name).scrollIntoView(true);
                            }
                        }
                    >
                        {recommendedSets[recommendedSet].name}
                    </div>
            {:else}
                No Kingdom Selected
            {/if}
        </h5>
        <button class="blueButton offset" style="--offset-top: -8px;"
            on:click={
                () => {
                    recommendedSet = Math.floor(Math.random() * recommendedSets.length)
                }
            }
        >
            Random Recommended Kingdom
        </button>
    </div>
    <CardDisplayOptions
        name="Recommended Kingdom Setup"
        illegalSortByOptions={["orderSent"]}
        inMenu=true
        bind:show={showCardDisplayOptions}
        bind:displayAs={displayAs}
        bind:sortByProperty={sortByProperty}
    />

    {#each recommendedSetsSorted as set, index}
        <div 
            class="panel {recommendedSet == index ? "selected" : ""}"
            id="{set.name}"
            on:click={
                () => {
                    recommendedSet = index;
                }
            }
        >
            <div class="title">
                <h4>{set.name}</h4>
                <p>{set.expansions.join(", ")}<p>
            </div>
            <div
                class="cards"
                class:displayAsRow={displayAs == "row"}
                class:displayAsGrid={displayAs == "grid"}
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
                    class:displayAsRow={displayAs == "row"}
                    class:displayAsGrid={displayAs == "grid"}
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
        padding-top: 35px;
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
        scroll-margin-top: 30px;
        border-bottom: var(--hrule);
    }

    .panel:hover:not(.selected) {
        background-color: color-mix(in srgb, var(--body-background-color), var(--blue-color) 20%);
    }
    
    .selected {
        background-color: color-mix(in srgb, var(--body-background-color), var(--blue-color) 50%);
    }

    .fakeLink {
        color: color-mix(in srgb, var(--blue-color), var(--text-color) 40%);
    }

    .fakeLink:hover {
        text-decoration: underline;
        cursor: pointer;
    }

    .selectionText {
        display: flex;
        flex-direction: row;
        gap: 6px;
    }

    .selectedKingdom {
        justify-content: center;
        display: flex;
        flex-direction: row;
        gap: 50px;
        padding-top: 70px;
        padding-bottom: 60px;
        border-bottom: var(--hrule);
    }

    .fa-gear {
        position: absolute;
        right: 20px;
        top: 20px;
        z-index: 999;
    }

    .fa-gear:hover {
        cursor: pointer;
    }

    .showCardDisplayOptions {
        color: var(--blue-color);
    }
</style>