import { Component } from '@angular/core';
import * as $ from 'jquery';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'lyrics-search-engine';
  result_boundary = 20;
  
  lan_selected;
  lan_selected_dict;
  retrievedLyrics = [];

  lan_dictionary_en = {
    'page-header': 'Sinhala Lyrics Search',
    'tab-label-1': 'Basic Search',
    'tab-label-2': 'Advanced Search',
    'basic-input-placeholder': 'Search Lyrics',
    'adv-input-label-1': 'Song Name',
    'adv-input-label-2': 'Artist',
    'adv-input-label-3': 'Genre',
    'adv-input-label-4': 'Written By',
    'adv-input-label-5': 'Music By',
    'adv-input-label-6': 'Key',
    'adv-input-label-7': 'Beat',
    'button': 'Search'
  }

  lan_dictionary_sn = {
    'page-header': 'සිංහල ගී පද',
    'tab-label-1': 'මූලික සෙවීම',
    'tab-label-2': 'උසස් සෙවීම',
    'basic-input-placeholder': 'පද රචනා සොයන්න',
    'adv-input-label-1': 'ගීතයේ නම',
    'adv-input-label-2': 'ගායකයා',
    'adv-input-label-3': 'Genre',
    'adv-input-label-4': 'පද රචනය',
    'adv-input-label-5': 'සංගීතය',
    'adv-input-label-6': 'Key',
    'adv-input-label-7': 'Beat',
    'button': 'සොයන්න'
  }

  ngOnInit() {
    this.lan_selected_dict = this.lan_dictionary_en

  }

  toggleLanguage() {
    if(this.lan_selected == 'en') {
      this.lan_selected = 'sn';
      this.lan_selected_dict = this.lan_dictionary_sn;
      $('.toggle-lan').removeClass('btn-primary');
      $('.toggle-lan').addClass('btn-success');
      $('.toggle-lan').html('සිංහල');
    } else {
      this.lan_selected = 'en';
      this.lan_selected_dict = this.lan_dictionary_en;
      $('.toggle-lan').removeClass('btn-success');
      $('.toggle-lan').addClass('btn-primary');
      $('.toggle-lan').html('English');
    }
  }

  lyricSearch() {
    this.retrievedLyrics = [];
    let query = $('#basic_search_query').val();

    $.ajax({
      type: "POST",
      url: "http://127.0.0.1:5002/basicsearch",
      data: {query: query, size: this.result_boundary, language: this.lan_selected},
      success: res => {
        console.log(res.hits.hits)
        let count = 0;

        res.hits.hits.forEach(element => {
          if(element._score > 100) {
            this.retrievedLyrics.push(element._source)
            count += 1
          }
        });

        if(this.retrievedLyrics.length == 0) {
          res.hits.hits.forEach(element => {
            if(element._score > 60) {
              this.retrievedLyrics.push(element._source)
              count += 1
            }
          });
        }
        if(this.retrievedLyrics.length == 0) {
          res.hits.hits.forEach(element => {
            if(count < this.result_boundary/2) {
              this.retrievedLyrics.push(element._source)
              count += 1
            }
          });
        }

      },
      error: err => {
        this.retrievedLyrics = [],
        console.log(err)
      }
    });

  }

}
