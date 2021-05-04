/* Extract all portfolio-item-wrapper elements*/ 
portfolioItems = document.querySelectorAll('.portfolio-item-wrapper');

/* Change background on hover*/
portfolioItems.forEach(portfolioItem => {
    /* Darken background*/
    portfolioItem.addEventListener('mouseover', () => {
        portfolioItem.childNodes[1].classList.add('img-darken');     
    })

    /*Revert to original*/
    portfolioItem.addEventListener('mouseout', () => {
        portfolioItem.childNodes[1].classList.remove('img-darken');     
    })
})
