<script>
    import {onMount} from "svelte";
    import {socket, activeCarousel} from "../stores.js";

    let tradeRoute = false;
    let prizes = false;

    onMount(
        () => {
            document.documentElement.setAttribute("sidebar-width", "64px");
        }
    );

    $: sections = [
        {
            title: "Played Cards",
            displayName: "Active",
            visible: true,
        },
        {
            title: "Your Hand",
            displayName: "Hand",
            visible: true,
        },
        {
            title: "Supply",
            displayName: "Supply",
            visible: true,
        },
        {
            title: "Your Discard Pile",
            displayName: "Discard",
            visible: true,
        },
        {
            title: "Trash",
            displayName: "Trash",
            visible: true,
        },
        {
            title: "Trade Route",
            displayName: "Trade Route",
            visible: tradeRoute,
        },
        {
            title: "Prizes",
            displayName: "Prizes",
            visible: prizes,
        },
    ]

    $socket.on(
        "display trade route",
        (_) => {
            tradeRoute = true;
        }
    );

    $socket.on(
        "display prizes",
        (_) => {
            prizes = true;
        }
    )
</script>

<main>
    {#each sections as section}
        {#if section.visible}
            <a 
                class="section {section.title == $activeCarousel ? "active" : ""}" 
                href="#{section.title}"
            >
                {section.displayName}
            </a>
        {/if}
    {/each}
    <a class="section" href="#Player Info">Players</a>
</main>

<style>
    main {
        z-index: 9999;
        left: 0;
        top: 0;
        width: 64px;
        height: 100%;
        position: fixed;
        background-color: var(--thead-background-color);
        color: var(--light-text-color);
        border-right: 1px solid var(--border-color);
        display: flex;
        flex-direction: column;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: space-around;
        align-items: stretch;
        font-family: var(--title-font-family);
    }

    /* Do not show sidebar on mobile devices */
    @media (max-width: 767px) {
        main {
             display: none;
        }
    }

    .section {
        justify-content: center;
        align-items: center;
        display: flex;
        writing-mode: vertical-lr;
        transform: rotate(180deg);
        font-weight: bold;
        flex-grow: 1;
        font-size: 20px;
    }

    .section.active {
        background-color: var(--blue-color);
        color: var(--dark-text-color);
    }

    .section:hover {
        background-color: color-mix(in srgb, var(--blue-color), #000000 20%);
    }

    .section.active:hover {
        color: ffcccc;
    }

    a {
        color: var(--light-text-color);
    }

    a:hover {
        text-decoration: none;
    }
</style>