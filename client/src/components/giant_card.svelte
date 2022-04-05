<script>
    export let name;
    export let effects;
    export let description;
    export let cost;
    export let type;
    export let quantity = null;

    let typeLowerCase = type.toLowerCase();

    $: action = typeLowerCase.includes("action") && !typeLowerCase.includes("attack") && !typeLowerCase.includes("reaction");
    $: attack = typeLowerCase.includes("attack")
    $: reaction = typeLowerCase.includes("reaction")
    $: victory = typeLowerCase.includes("victory");
    $: curse = typeLowerCase.includes("curse");
    $: treasure = typeLowerCase.includes("treasure");
    $: basicTreasure = ["Copper", "Silver", "Gold", "Platinum"].includes(name);
    $: basicVictory = ["Curse", "Estate", "Duchy", "Province", "Colony"].includes(name);

    function renderText(text) {
        return text
            .replace("$", `<i class="fa-solid fa-coins"></i>`)
            .replace("victory points", `<i class="bi bi-shield-shaded"></i>`)
            .replace("victory point", `<i class="bi bi-shield-shaded"></i>`);
    }

    $: renderedEffects = effects.map(renderText);
    $: renderedDescription = description.map(renderText);
</script>

<main 
    class:action
    class:attack
    class:reaction
    class:victory
    class:curse
    class:treasure
    class:basicTreasure
    class:basicVictory
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
    <ul class="description">
        {#each renderedDescription as description}
            <li>{@html description}</li>
        {/each}
    </ul>
    <div class="footer">
        <div class="cost">{cost}&nbsp;<i class="fa-solid fa-coins"></i></div>
        <div class="type">{type}</div>
    </div>
</main>

<style lang="scss">
    @import url("https://use.typekit.net/ktm4syd.css");

    $multiplier: 3;

    $ratio: 1.618;
    $width:  $multiplier * 200px;
    $height: $multiplier * $width * $ratio;

    $padding: $multiplier * 10px;
    $padding-basis: $multiplier * 15px;
    $header-padding: 0px 0px $multiplier * $padding-basis 0px;
    $corner-radius: $multiplier * 20px;
    $margin: $multiplier * 5px;

    $shadow-color: rgba(127, 145, 163, 0.5);
    $shadow: 1px 1px 4px 4px $shadow-color;

    $font-size: $multiplier * 16px;
    $dark-text-color: #343338;
    $light-text-color: #dadada;
    $point: #100e17;
    $point-light: rgb(33, 29, 47);

    main {
        border: 1px solid slategrey;
        display: flex;
        flex: 0 0 $width;
        width: $width;
        height: $height;
        max-height: 90vh;
        font-size: $font-size;
        color: $light-text-color;
        flex-direction: column;
        padding: $padding;
        margin-right: $margin;
        border-radius: $corner-radius;
        box-shadow: $shadow;
        position: relative;
        overflow-y: hidden;
        overflow-x: hidden;
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

    .basicTreasure .description {
        padding-top: 40px;
        font-size: 60px;
    }
    .basicVictory .description {
        padding-top: 40px;
        font-size: 60px;
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
        list-style-type: none;
        padding: 0;
        margin-left: 0;
        margin-bottom: $padding-basis;
        // text-align: left;
        overflow-y: auto;
    }

    .description li:not(:last-child) { 
        margin-bottom: 10px;  
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