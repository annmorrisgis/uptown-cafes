$(document).ready(function() {
  var map = L.map('map').setView([40.834167, -73.947222], 15);
  var html = '';
  var phone = '';
  var ratingImage = '';

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
  }).addTo(map);

  $.ajax({
    dataType: "json",
    url: "cafes.json",
    success: function (data) {
      for (var item in data) {
        if (data[item].phone) {
          data[item].phone = data[item].phone.substr(0,2) + '-' + data[item].phone.substr(2,3) + '-' + data[item].phone.substr(5,3) + '-' + data[item].phone.substr(8,4);
        }
        data[item].name = '<a class="popup-name" target="_blank" href="' + data[item].URL + '">' + data[item].name + '</a>';
        switch (data[item].rating) {
          case 1:
            ratingImage = 'small_1.png';
            break;
          case 1.5:
            ratingImage = 'small_1_half.png';
            break;
          case 2:
            ratingImage = 'small_2.png';
            break;
          case 2.5:
            ratingImage = 'small_2_half.png';
            break;
          case 3:
            ratingImage = 'small_3.png';
            break;
          case 3.5:
            ratingImage = 'small_3_half.png';
            break;
          case 4:
            ratingImage = 'small_4.png';
            break;
          case 4.5:
            ratingImage = 'small_4_half.png';
            break;
          default:
            ratingImage = 'small_5.png';
            break;
        }
        if (data[item].imageURL) {
          html += '<div class="popup-content with-image"><div class="popup-image"><img src="' + data[item].imageURL + '" /></div>';
        } else {
          html += '<div class="popup-content">';
        }
        html += '<div class="popup-text"><div><strong>' + data[item].name + '</strong></div><div>' + data[item].address[0] + '</div><div>' + data[item].address[1] + '</div><div>' + data[item].phone + '</div><div><img class="rating" src="images/small-yelp-stars/' + ratingImage + '" alt="stars" /> (' + data[item].reviewCount + ')</div></div>';
        if (data[item].imageURL) {
          html += '<div class="clear"></div>';
        }
        html += '</div>';
        L.marker([data[item].latitude,data[item].longitude]).addTo(map).bindPopup(html)
        html = "";
      }
    }
   });
});
