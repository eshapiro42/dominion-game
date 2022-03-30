<script>
    import {createEventDispatcher} from "svelte";
    import {fade} from 'svelte/transition';
    
    const dispatch = createEventDispatcher();
    
    import GiantCard from "./giant_card.svelte";
    import Modal from "./modal.svelte";

    export let name;
    export let effects;
    export let description;
    export let cost;
    export let type;
    export let id;
    export let quantity = null;
    export let waitingForSelection; 
    export let numSelected;
    export let selected = false;

    let typeLowerCase = type.toLowerCase();
    let hovering = false;
    let hoveringTimeout = null;

    $: action = typeLowerCase.includes("action") && !typeLowerCase.includes("attack") && !typeLowerCase.includes("reaction");
    $: attack = typeLowerCase.includes("attack")
    $: reaction = typeLowerCase.includes("reaction")
    $: victory = typeLowerCase.includes("victory");
    $: curse = typeLowerCase.includes("curse");
    $: treasure = typeLowerCase.includes("treasure");

    function renderText(text) {
        return text.replace("$", `<i class="fa-solid fa-coins"></i>`);
    }

    $: renderedEffects = effects.map(renderText);
    $: renderedDescription = renderText(description);

    function clicked() {
        if (hoveringTimeout != null) {
            clearTimeout(hoveringTimeout);
            hoveringTimeout = null;
        }
        if (waitingForSelection.value && type.toLowerCase().includes(waitingForSelection.type)) {
            if (
                // Don't allow selection if the maximum number of cards is already selected (unselection is fine)
                (!selected && waitingForSelection.maxCards != null && numSelected >= waitingForSelection.maxCards)
                ||
                // Don't allow selection if the card costs more than the maximum cost
                (!selected && waitingForSelection.maxCost != null && cost > waitingForSelection.maxCost)
            ) {
                return;
            }
            selected = !selected;
            dispatch(
                "clicked", 
                {
                    name: name,
                    effects: effects,
                    description: description,
                    cost: cost,
                    type: type,
                    id: id,
                    selected: selected,
                }
            )
        }
    }

    $: if (waitingForSelection != null && !waitingForSelection.value) {
        selected = false;
    }

</script>

<Modal 
    show={hovering}
    on:click = {
        () => {
            hovering = false;
        }
    }
>
    <span slot="contents">
        <GiantCard
            {name}
            {effects}
            {description}
            {cost}
            {type}
            {id}
            {quantity}
        />
    </span>
</Modal>

<main
    in:fade
    out:fade
    on:click={clicked}
    on:dblclick={
        () => {
            hovering = true;
        }
    }
    class:action
    class:attack
    class:reaction
    class:victory
    class:curse
    class:treasure
    class:selected
>
    {#if quantity == null}
        <div class="name">{name}</div>
    {:else if quantity == "inf"}
        <div class="name">{name} &ndash &#8734;</div>
    {:else}
        <div class="name">{name} &ndash {quantity}</div>
    {/if}
    <ul class="effects">
        {#each renderedEffects as effect}
            <li>{@html effect}</li>
        {/each}
    </ul>
    <div class="description">{@html renderedDescription}</div>
    <div class="footer">
        <div class="cost">{cost}&nbsp;<i class="fa-solid fa-coins"></i></div>
        <div class="type">{type}</div>
    </div>
</main>

<style lang="scss">
    @import url("https://use.typekit.net/ktm4syd.css");

    $ratio: 1.618;
    $width: 200px;
    $height: $width * $ratio;

    $padding: 10px;
    $padding-basis: 15px;
    $header-padding: 0px 0px $padding-basis 0px;
    $corner-radius: 20px;
    $margin: 5px;

    $shadow-color: rgba(127, 145, 163, 0.5);
    $shadow: 1px 1px 4px 4px $shadow-color;

    $font-size: 16px;
    $dark-text-color: #343338;
    $light-text-color: #dadada;
    $point: #100e17;
    $point-light: rgb(33, 29, 47);

    $giant-card-linear-multiplier: 2;
    $giant-card-width: $giant-card-linear-multiplier * $width;
    $giant-card-height: $giant-card-linear-multiplier * $height;
    $giant-font-size: $giant-card-linear-multiplier * $font-size;
    $giant-card-padding: $giant-card-linear-multiplier * $padding;
    $giant-card-padding-basis: $giant-card-linear-multiplier * $padding-basis;
    $giant-card-header-padding: 0px 0px $giant-card-linear-multiplier * $padding-basis 0px;
    $giant-card-corner-radius: $giant-card-linear-multiplier * $corner-radius;
    $giant-card-margin: $giant-card-linear-multiplier * $margin;


    main {
        border: 1px solid slategrey;
        display: flex;
        flex: 0 0 auto;
        position: relative;
        width: $width;
        min-height: $height;
        max-height: $height;
        font-size: $font-size;
        color: $light-text-color;
        flex-direction: column;
        padding: $padding;
        margin-right: $margin;
        border-radius: $corner-radius;
        box-shadow: $shadow;
        transition: 0.4s ease-out;
        position: relative;
        left: 0px;
        right: 50px;
        overflow-y: hidden;
        overflow-x: hidden;
    }

    main:hover {
        transform: translateY(-20px);
        transition: 0.4s ease-out;
        transition-delay: 0.1s;
    }

    // .hovering {
    //     position: fixed;
    //     margin: auto;
    //     width: $giant-card-width;
    //     min-height: $giant-card-height;
    //     font-size: $giant-font-size;
    //     padding: $giant-card-padding;
    //     border-radius: $giant-card-corner-radius;
    //     margin-right: $giant-card-margin;
    //     z-index: 1000;
    // }

    .selected {
        border: 3px solid red;
        transform: translateY(-20px);
        transition: 0.4s ease-out;
    }

    .action {
        background-color: #343338;
        color: $light-text-color;
    }

    .attack {
        background-color: #ffcccc;
        color: $dark-text-color;
    }

    .reaction {
        background-color: #80bfff;
        color: $dark-text-color;
    }

    .victory {
        background-color: #c1f0c1;
        color: $dark-text-color;
    }

    .curse {
        background-color: #dab3ff;
        color: $dark-text-color;
    }

    .treasure {
        background-color: #fff0b3;
        color: $dark-text-color;
    }

    .name {
        display: flex;
        justify-content: space-between;
        width: $width;
        padding: $header-padding;
    }

    .effects {
        font-family: minion-pro, serif;
        font-weight: 700;
        font-style: normal;
        list-style-type: none;
        padding: 0;
        margin-bottom: $padding-basis;
        margin-left: 0;
    }

    .description {
        font-family: minion-pro, serif;
        font-weight: 400;
        font-style: normal;
        margin-bottom: $padding-basis;
        // text-align: left;
        overflow-y: auto;
    }

    .footer {
        display: flex;
        justify-content: space-between;
        position: absolute;
        width: $width;
        bottom: $margin;
        margin-top: $padding-basis;
        padding-right: $padding-basis + 4px;
    }
</style>